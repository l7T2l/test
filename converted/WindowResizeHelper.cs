// ═══════════════════════════════════════════════════════════════════════════════
// WindowResizeHelper.cs - تغيير حجم النافذة من الحواف
// المقابل لـ: main.py start_resize_if_at_edge (1638-1663),
//             handle_mouse_move_for_resize (1665-1732), end_resize (1734-1744)
// تحويل سطر بسطر - كل حد ونمط resize مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Windows;
using System.Windows.Input;
using Window = System.Windows.Window;
using Point = System.Windows.Point;
using Cursors = System.Windows.Input.Cursors;
using Cursor = System.Windows.Input.Cursor;

namespace SmartKeyboard
{
    // ═══════════════════════════════════════════════════════════════
    // WindowResizeHelper - إدارة resize من 8 اتجاهات
    // السطور 1638-1744
    // ═══════════════════════════════════════════════════════════════
    public class WindowResizeHelper
    {
        private readonly Window _window;
        private readonly Action? _onResizeStart;
        private readonly Action? _onResizeEnd;

        // السطور 1146-1149: Resize State
        private string _resizeMode = "";         // السطر 1648
        private Point? _resizeStartPos = null;   // السطر 1659
        private Rect? _resizeStartGeo = null;    // السطر 1660

        // السطر 1641: Resize margin
        private const int RESIZE_MARGIN = 15;

        // السطور 1701-1702: Minimum constraints
        private const int MIN_WIDTH = 15;
        private const int MIN_HEIGHT = 15;

        public WindowResizeHelper(Window window, Action? onResizeStart = null, Action? onResizeEnd = null)
        {
            _window = window;
            _onResizeStart = onResizeStart;
            _onResizeEnd = onResizeEnd;
        }

        // ═══════════════════════════════════════════════════════════════
        // start_resize_if_at_edge - السطور 1638-1663
        // Check if click is at edge and start resize. Returns True if resize started.
        // ═══════════════════════════════════════════════════════════════
        public bool StartResizeIfAtEdge(Point pos, Point globalPos)
        {
            double w = _window.ActualWidth;
            double h = _window.ActualHeight;

            // السطور 1643-1646
            bool left = pos.X < RESIZE_MARGIN;
            bool right = pos.X > w - RESIZE_MARGIN;
            bool top = pos.Y < RESIZE_MARGIN;
            bool bottom = pos.Y > h - RESIZE_MARGIN;

            // السطور 1648-1656: Determine resize mode
            _resizeMode = "";
            if (top && left) _resizeMode = "tl";
            else if (top && right) _resizeMode = "tr";
            else if (bottom && left) _resizeMode = "bl";
            else if (bottom && right) _resizeMode = "br";
            else if (top) _resizeMode = "t";
            else if (bottom) _resizeMode = "b";
            else if (left) _resizeMode = "l";
            else if (right) _resizeMode = "r";

            // السطور 1658-1662
            if (!string.IsNullOrEmpty(_resizeMode))
            {
                _resizeStartPos = globalPos;
                _resizeStartGeo = new Rect(_window.Left, _window.Top, _window.Width, _window.Height);
                _onResizeStart?.Invoke();  // Lock buttons - السطر 1661
                return true;
            }
            return false;
        }

        // ═══════════════════════════════════════════════════════════════
        // handle_mouse_move_for_resize - السطور 1665-1732
        // Update cursor and handle resizing.
        // ═══════════════════════════════════════════════════════════════
        public void HandleMouseMoveForResize(Point pos, Point globalPos)
        {
            double w = _window.ActualWidth;
            double h = _window.ActualHeight;

            // السطور 1670-1684: Determine cursor shape based on position
            bool left = pos.X < RESIZE_MARGIN;
            bool right = pos.X > w - RESIZE_MARGIN;
            bool top = pos.Y < RESIZE_MARGIN;
            bool bottom = pos.Y > h - RESIZE_MARGIN;

            Cursor cursorShape = Cursors.Arrow;
            if ((top && left) || (bottom && right))
                cursorShape = Cursors.SizeNWSE;  // SizeFDiagCursor
            else if ((top && right) || (bottom && left))
                cursorShape = Cursors.SizeNESW;  // SizeBDiagCursor
            else if (top || bottom)
                cursorShape = Cursors.SizeNS;    // SizeVerCursor
            else if (left || right)
                cursorShape = Cursors.SizeWE;    // SizeHorCursor

            // السطور 1686-1692: Update cursor
            if (cursorShape != Cursors.Arrow)
            {
                _window.Cursor = cursorShape;
            }
            else
            {
                _window.Cursor = Cursors.Arrow;
            }

            // السطور 1694-1732: Handle active resize
            if (!string.IsNullOrEmpty(_resizeMode) && _resizeStartPos.HasValue && _resizeStartGeo.HasValue)
            {
                var delta = new Point(globalPos.X - _resizeStartPos.Value.X, globalPos.Y - _resizeStartPos.Value.Y);
                var geo = _resizeStartGeo.Value;
                double x = geo.X, y = geo.Y, newW = geo.Width, newH = geo.Height;

                // السطور 1704-1726: Apply resize based on mode with minimum constraints
                if (_resizeMode.Contains('r'))
                {
                    newW = Math.Max(MIN_WIDTH, geo.Width + delta.X);
                }

                if (_resizeMode.Contains('l'))
                {
                    double calcW = Math.Max(MIN_WIDTH, geo.Width - delta.X);
                    if (calcW > MIN_WIDTH)
                    {
                        x = geo.X + delta.X;
                    }
                    else
                    {
                        x = geo.X + geo.Width - MIN_WIDTH;
                    }
                    newW = calcW;
                }

                if (_resizeMode.Contains('b'))
                {
                    newH = Math.Max(MIN_HEIGHT, geo.Height + delta.Y);
                }

                if (_resizeMode.Contains('t'))
                {
                    double calcH = Math.Max(MIN_HEIGHT, geo.Height - delta.Y);
                    if (calcH > MIN_HEIGHT)
                    {
                        y = geo.Y + delta.Y;
                    }
                    else
                    {
                        y = geo.Y + geo.Height - MIN_HEIGHT;
                    }
                    newH = calcH;
                }

                // السطور 1728-1732: Apply geometry
                _window.Left = x;
                _window.Top = y;
                _window.Width = newW;
                _window.Height = newH;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // end_resize - السطور 1734-1744
        // End resize operation and save config.
        // ═══════════════════════════════════════════════════════════════
        public void EndResize()
        {
            if (!string.IsNullOrEmpty(_resizeMode))
            {
                // السطور 1737-1740: Save config
                CONFIG.Instance.X = (int)_window.Left;
                CONFIG.Instance.Y = (int)_window.Top;
                CONFIG.Instance.W = (int)_window.Width;
                CONFIG.Instance.H = (int)_window.Height;

                _resizeMode = "";
                _resizeStartPos = null;
                _resizeStartGeo = null;
                _window.Cursor = Cursors.Arrow;

                // السطر 1744: Unlock buttons
                _onResizeEnd?.Invoke();
            }
        }

        // Check if currently resizing
        public bool IsResizing => !string.IsNullOrEmpty(_resizeMode);
    }
}
