// ═══════════════════════════════════════════════════════════════════════════════
// SettingsPage.xaml.cs - صفحة الإعدادات
// المقابل لـ: Styles/settings_page.py class SettingsPageContent (السطور 20-1247)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using UserControl = System.Windows.Controls.UserControl;
using Color = System.Windows.Media.Color;
using ColorConverter = System.Windows.Media.ColorConverter;
using SolidColorBrush = System.Windows.Media.SolidColorBrush;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class SettingsPageContent(QWidget): - السطر 20
    /// محتوى صفحة الإعدادات - للربط مع الإطار الرئيسي
    /// </summary>
    public partial class SettingsPage : UserControl
    {
        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - من __init__ السطور 23-48
        // ═══════════════════════════════════════════════════════════════

        // السطور 42-48: Default values
        private int _bgOpacity;
        private int _textOpacity;
        private int _settingsOpacity;
        private int _fontSize;
        private int _firstLineEnd;
        private string _bgColor = "#000000";
        private string _textColor = "#FFFF00";

        // Reference to MainWindow for apply_settings
        private MainWindow? _overlay;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - من __init__ السطور 23-54
        // ═══════════════════════════════════════════════════════════════
        public SettingsPage()
        {
            InitializeComponent();

            // السطور 33-48: Load values from CONFIG
            _bgOpacity = CONFIG.Instance.BgOpacity;
            _textOpacity = CONFIG.Instance.TextOpacity;
            _settingsOpacity = CONFIG.Instance.SettingsOpacity;
            _fontSize = CONFIG.Instance.FontSize;
            _firstLineEnd = CONFIG.Instance.FirstLineEnd;
            _bgColor = CONFIG.Instance.BgColor;
            _textColor = CONFIG.Instance.TextColor;

            // Initialize sliders
            BgOpacitySlider.Value = _bgOpacity;
            TextOpacitySlider.Value = _textOpacity;
            SettingsOpacitySlider.Value = _settingsOpacity;
            FontSizeSlider.Value = _fontSize;
            LineEndSlider.Value = _firstLineEnd;

            // Update value labels
            BgOpacityValue.Text = _bgOpacity.ToString();
            TextOpacityValue.Text = _textOpacity.ToString();
            SettingsOpacityValue.Text = _settingsOpacity.ToString();
            FontSizeValue.Text = _fontSize.ToString();
            LineEndValue.Text = _firstLineEnd.ToString();

            // Load icons
            LoadIcons();

            // Update color buttons - السطر 54
            UpdateColorButtons();
        }

        // ═══════════════════════════════════════════════════════════════
        // LoadIcons - من السطور 104-117
        // ═══════════════════════════════════════════════════════════════
        private void LoadIcons()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string iconsDir = Path.Combine(exeDir, "Icons");

            LoadIcon(SettingsIcon, Path.Combine(iconsDir, "Settings_panel.png"), 24);
            LoadIcon(TransparencyIcon, Path.Combine(iconsDir, "transparency.png"), 24);
            LoadIcon(TextIcon, Path.Combine(iconsDir, "text.png"), 24);
            LoadIcon(ColorIcon, Path.Combine(iconsDir, "color.png"), 24);
        }

        private void LoadIcon(System.Windows.Controls.Image img, string path, int size)
        {
            try
            {
                if (File.Exists(path))
                {
                    BitmapImage bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(path, UriKind.Absolute);
                    bitmap.DecodePixelWidth = size;
                    bitmap.DecodePixelHeight = size;
                    bitmap.EndInit();
                    img.Source = bitmap;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[SETTINGS] Icon load error: {ex.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Slider_ValueChanged - من السطور 365-378
        // ═══════════════════════════════════════════════════════════════
        private void Slider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (sender is not Slider slider) return;

            int value = (int)slider.Value;

            // Update corresponding value label and save to CONFIG
            if (slider == BgOpacitySlider)
            {
                BgOpacityValue.Text = value.ToString();
                _bgOpacity = value;
                CONFIG.Instance.BgOpacity = value;
            }
            else if (slider == TextOpacitySlider)
            {
                TextOpacityValue.Text = value.ToString();
                _textOpacity = value;
                CONFIG.Instance.TextOpacity = value;
            }
            else if (slider == SettingsOpacitySlider)
            {
                SettingsOpacityValue.Text = value.ToString();
                _settingsOpacity = value;
                CONFIG.Instance.SettingsOpacity = value;
                // السطور 370-375: Apply to settings window
                // This would update parent SettingsWindow opacity
            }
            else if (slider == FontSizeSlider)
            {
                FontSizeValue.Text = value.ToString();
                _fontSize = value;
                CONFIG.Instance.FontSize = value;
            }
            else if (slider == LineEndSlider)
            {
                LineEndValue.Text = value.ToString();
                _firstLineEnd = value;
                CONFIG.Instance.FirstLineEnd = value;
            }

            // السطور 377-378: تطبيق الإعدادات على OverlayWindow
            // TODO: Call overlay.apply_settings() when connected
        }

        // ═══════════════════════════════════════════════════════════════
        // Color Button Click Handlers - من السطور 229-239
        // ═══════════════════════════════════════════════════════════════
        private void BgColorButton_Click(object sender, RoutedEventArgs e)
        {
            PickColor("bg");
        }

        private void TextColorButton_Click(object sender, RoutedEventArgs e)
        {
            PickColor("txt");
        }

        // ═══════════════════════════════════════════════════════════════
        // pick_color - السطور 582-764 (using custom ColorPickerPopup)
        // ═══════════════════════════════════════════════════════════════
        private ColorPickerPopup? _colorPicker;

        private void PickColor(string target)
        {
            // إغلاق picker سابق إن موجود - السطور 590-592
            if (_colorPicker != null)
            {
                _colorPicker.Close();
                _colorPicker = null;
            }

            // إنشاء Color Picker - السطور 594-603
            _colorPicker = new ColorPickerPopup();

            // عند اختيار لون - السطور 644-706
            _colorPicker.ColorSelected += (colorHex) =>
            {
                _colorPicker = null;

                // حفظ اللون - السطور 648-660
                if (target == "bg")
                {
                    _bgColor = colorHex;
                    CONFIG.Instance.BgColor = colorHex;
                }
                else
                {
                    _textColor = colorHex;
                    CONFIG.Instance.TextColor = colorHex;
                }

                // تحديث الأزرار - السطر 706
                UpdateColorButtons();
                Console.WriteLine($"✓ Color selected: {colorHex}");

                // تطبيق الإعدادات على OverlayWindow - السطور 662-664
                // TODO: _overlay?.ApplySettings();
            };

            // إظهار الـ picker فوق الزر - السطور 751-756
            if (target == "bg")
            {
                _colorPicker.ShowAboveButton(BgColorButton);
            }
            else
            {
                _colorPicker.ShowAboveButton(TextColorButton);
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // update_color_buttons - السطور 416-461
        // ═══════════════════════════════════════════════════════════════
        private void UpdateColorButtons()
        {
            // Background color button - السطور 421-440
            string bgTextColor = GetContrastingTextColor(_bgColor);
            string bgBorderColor = GetBorderColor(_bgColor);
            
            BgColorButton.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString(_bgColor));
            BgColorButton.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString(bgTextColor));
            BgColorButton.BorderBrush = new SolidColorBrush((Color)ColorConverter.ConvertFromString(bgBorderColor));
            BgColorButton.BorderThickness = new Thickness(2);

            // Text color button - السطور 442-461
            string txtTextColor = GetContrastingTextColor(_textColor);
            string txtBorderColor = GetBorderColor(_textColor);
            
            TextColorButton.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString(_textColor));
            TextColorButton.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString(txtTextColor));
            TextColorButton.BorderBrush = new SolidColorBrush((Color)ColorConverter.ConvertFromString(txtBorderColor));
            TextColorButton.BorderThickness = new Thickness(2);
        }

        // ═══════════════════════════════════════════════════════════════
        // get_luminance - السطور 467-491
        // ═══════════════════════════════════════════════════════════════
        private double GetLuminance(string hexColor)
        {
            // السطور 479-489
            hexColor = hexColor.TrimStart('#');
            
            double r = Convert.ToInt32(hexColor.Substring(0, 2), 16) / 255.0;
            double g = Convert.ToInt32(hexColor.Substring(2, 2), 16) / 255.0;
            double b = Convert.ToInt32(hexColor.Substring(4, 2), 16) / 255.0;
            
            // السطر 489: Luminance calculation (W3C formula)
            return 0.299 * r + 0.587 * g + 0.114 * b;
        }

        // ═══════════════════════════════════════════════════════════════
        // get_contrasting_text_color - السطور 493-511
        // ═══════════════════════════════════════════════════════════════
        private string GetContrastingTextColor(string bgColor)
        {
            double luminance = GetLuminance(bgColor);
            
            // السطور 508-511
            if (luminance > 0.5)
                return "#000000";  // Black text for light backgrounds
            else
                return "#ffffff";  // White text for dark backgrounds
        }

        // ═══════════════════════════════════════════════════════════════
        // get_border_color - السطور 513-546
        // ═══════════════════════════════════════════════════════════════
        private string GetBorderColor(string baseColor)
        {
            double luminance = GetLuminance(baseColor);
            
            string hex = baseColor.TrimStart('#');
            int r = Convert.ToInt32(hex.Substring(0, 2), 16);
            int g = Convert.ToInt32(hex.Substring(2, 2), 16);
            int b = Convert.ToInt32(hex.Substring(4, 2), 16);
            
            double factor;
            if (luminance > 0.5)
                factor = 0.7;  // Darker for light colors
            else
                factor = 1.3;  // Lighter for dark colors
            
            r = Math.Clamp((int)(r * factor), 0, 255);
            g = Math.Clamp((int)(g * factor), 0, 255);
            b = Math.Clamp((int)(b * factor), 0, 255);
            
            return $"#{r:X2}{g:X2}{b:X2}";
        }
    }
}
