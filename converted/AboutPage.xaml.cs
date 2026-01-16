// ═══════════════════════════════════════════════════════════════════════════════
// AboutPage.xaml.cs - صفحة حول البرنامج
// المقابل لـ: Styles/about_page.py class AboutPageContent (السطور 29-177)
// تحويل سطر بسطر - كل ستايل وكل عنصر مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Windows.Media.Imaging;
using UserControl = System.Windows.Controls.UserControl;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class AboutPageContent(QWidget): - السطر 29
    /// محتوى صفحة حول - للربط مع الإطار الرئيسي
    /// </summary>
    public partial class AboutPage : UserControl
    {
        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - من __init__ السطور 32-34
        // ═══════════════════════════════════════════════════════════════
        public AboutPage()
        {
            InitializeComponent();

            // Setup UI - السطر 34: self.setup_ui()
            SetupUI();
        }

        // ═══════════════════════════════════════════════════════════════
        // setup_ui - السطور 36-177
        // ═══════════════════════════════════════════════════════════════
        private void SetupUI()
        {
            // السطور 47-57: تحميل الشعار
            LoadLogo();

            // السطر 153: ver_lbl = QLabel(f"v{VERSION}")
            VerLbl.Text = $"v{Version.VERSION}";
        }

        // ═══════════════════════════════════════════════════════════════
        // Load Logo - السطور 44-58
        // ═══════════════════════════════════════════════════════════════
        private void LoadLogo()
        {
            try
            {
                // السطور 47-48: تحديد مسار الشعار
                string exeDir = AppDomain.CurrentDomain.BaseDirectory;
                string logoPath = Path.Combine(exeDir, "Icons", "app_256.png");

                // السطور 50-57: تحميل وعرض الشعار
                if (File.Exists(logoPath))
                {
                    BitmapImage bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(logoPath, UriKind.Absolute);
                    bitmap.DecodePixelWidth = 100;  // السطر 51: logo_size = 100
                    bitmap.DecodePixelHeight = 100;
                    bitmap.EndInit();

                    LogoImage.Source = bitmap;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ABOUT] Logo load error: {ex.Message}");
            }
        }
    }
}
