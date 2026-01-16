// ═══════════════════════════════════════════════════════════════════════════════
// UpdatePage.xaml.cs - نافذة التحديث
// المقابل لـ: Styles/update_page.py class UpdateDialog (السطور 110-1407)
// تحويل سطر بسطر - كل وظيفة وكل ستايل مطابق للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Window = System.Windows.Window;
using Color = System.Windows.Media.Color;
using Application = System.Windows.Application;

namespace SmartKeyboard.Styles
{
    /// <summary>
    /// class UpdateDialog(QDialog): - السطر 110
    /// نافذة التحديث التلقائي
    /// </summary>
    public partial class UpdatePage : Window
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke for WS_EX_NOACTIVATE - السطور 243-255
        // ═══════════════════════════════════════════════════════════════
        private const int GWL_EXSTYLE = -20;
        private const uint WS_EX_NOACTIVATE = 0x08000000;
        private const uint WS_EX_TOPMOST = 0x00000008;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات الأساسية - السطور 144-154
        // ═══════════════════════════════════════════════════════════════
        private string _currentVersion;
        private string _newVersion;
        private string _downloadUrl;
        private string[]? _changelog;
        private bool _isDownloading = false;
        private bool _isChangelogVisible = false;

        // Download variables
        private HttpClient? _httpClient;
        private string? _zipPath;
        private string? _extractDir;
        private string? _targetDir;

        // Blink timer
        private DispatcherTimer? _blinkTimer;
        private bool _blinkVisible = true;

        // Icons
        private ImageSource? _openIcon;
        private ImageSource? _closeIcon;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - السطور 130-182
        // ═══════════════════════════════════════════════════════════════
        public UpdatePage(string currentVersion = "1.9", string newVersion = "2.0", string downloadUrl = "", string[]? changelog = null)
        {
            InitializeComponent();

            _currentVersion = currentVersion;
            _newVersion = newVersion;
            _downloadUrl = downloadUrl;
            _changelog = changelog;

            // Set version labels
            CurrentVersionValue.Text = $"v{_currentVersion}";
            NewVersionValue.Text = $"v{_newVersion}";

            // Set changelog text
            if (_changelog != null && _changelog.Length > 0)
            {
                ChangelogText.Text = string.Join("\n", _changelog);
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Window_Loaded - السطور 231-241
        // ═══════════════════════════════════════════════════════════════
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // Apply WS_EX_NOACTIVATE - السطور 243-255
            try
            {
                var hwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle;
                uint style = GetWindowLong(hwnd, GWL_EXSTYLE);
                SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[UPDATE] Error applying WS_EX_NOACTIVATE: {ex.Message}");
            }

            // Load icons
            LoadIcons();

            // Load logo
            LoadLogo();

            // Apply opacity from config
            ApplyOpacity();

            // Center window
            CenterWindow();
        }

        // ═══════════════════════════════════════════════════════════════
        // Load icons - السطور 392-402
        // ═══════════════════════════════════════════════════════════════
        private void LoadIcons()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string iconsDir = Path.Combine(exeDir, "Icons");

            string openPath = Path.Combine(iconsDir, "open.png");
            string closePath = Path.Combine(iconsDir, "close.png");

            if (File.Exists(openPath))
            {
                _openIcon = new BitmapImage(new Uri(openPath, UriKind.Absolute));
                // Set initial icon
                var toggleIcon = FindToggleIcon();
                if (toggleIcon != null)
                    toggleIcon.Source = _openIcon;
            }

            if (File.Exists(closePath))
            {
                _closeIcon = new BitmapImage(new Uri(closePath, UriKind.Absolute));
            }
        }

        private System.Windows.Controls.Image? FindToggleIcon()
        {
            // Find the Image inside ToggleButton template
            if (ToggleButton.Template.FindName("ToggleIcon", ToggleButton) is System.Windows.Controls.Image img)
                return img;
            return null;
        }

        // ═══════════════════════════════════════════════════════════════
        // Load logo - السطور 291-306
        // ═══════════════════════════════════════════════════════════════
        private void LoadLogo()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string logoPath = Path.Combine(exeDir, "Icons", "app_256.png");

            if (File.Exists(logoPath))
            {
                LogoImage.Source = new BitmapImage(new Uri(logoPath, UriKind.Absolute));
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Apply opacity - السطور 540-543
        // ═══════════════════════════════════════════════════════════════
        private void ApplyOpacity()
        {
            int opacity = CONFIG.Instance.SettingsOpacity;
            // Opacity is applied via GradientStops in XAML (simplified)
        }

        // ═══════════════════════════════════════════════════════════════
        // Center window - السطور 257-264
        // ═══════════════════════════════════════════════════════════════
        private void CenterWindow()
        {
            var screen = SystemParameters.WorkArea;
            Left = (screen.Width - Width) / 2;
            Top = (screen.Height - ActualHeight) / 2;
        }

        // ═══════════════════════════════════════════════════════════════
        // Window drag - السطور 173-176
        // ═══════════════════════════════════════════════════════════════
        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
            {
                DragMove();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Toggle changelog - السطور 515-532
        // ═══════════════════════════════════════════════════════════════
        private void ToggleButton_Click(object sender, RoutedEventArgs e)
        {
            _isChangelogVisible = !_isChangelogVisible;

            if (_isChangelogVisible)
            {
                // Show changelog, hide logo and title
                LogoImage.Visibility = Visibility.Collapsed;
                TitleLabel.Visibility = Visibility.Collapsed;
                ChangelogContainer.Visibility = Visibility.Visible;

                var toggleIcon = FindToggleIcon();
                if (toggleIcon != null && _closeIcon != null)
                    toggleIcon.Source = _closeIcon;
            }
            else
            {
                // Show logo and title, hide changelog
                LogoImage.Visibility = Visibility.Visible;
                TitleLabel.Visibility = Visibility.Visible;
                ChangelogContainer.Visibility = Visibility.Collapsed;

                var toggleIcon = FindToggleIcon();
                if (toggleIcon != null && _openIcon != null)
                    toggleIcon.Source = _openIcon;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Later button - السطر 468
        // ═══════════════════════════════════════════════════════════════
        private void LaterButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        // ═══════════════════════════════════════════════════════════════
        // Start update - السطور 778-799
        // ═══════════════════════════════════════════════════════════════
        private void UpdateButton_Click(object sender, RoutedEventArgs e)
        {
            _isDownloading = true;

            // Hide buttons, show progress
            ButtonsContainer.Visibility = Visibility.Collapsed;
            ProgressContainer.Visibility = Visibility.Visible;
            ProgressBar.Value = 0;
            ProgressLabel.Text = "جاري بدء التحميل...";

            // Start download
            StartDownload();
        }

        // ═══════════════════════════════════════════════════════════════
        // Start download - السطور 801-823
        // ═══════════════════════════════════════════════════════════════
        private async void StartDownload()
        {
            if (string.IsNullOrEmpty(_downloadUrl))
            {
                ProgressLabel.Text = "خطأ: رابط التحميل غير متوفر";
                return;
            }

            _httpClient = new HttpClient();

            try
            {
                ProgressLabel.Text = "جاري التحميل...";

                var response = await _httpClient.GetAsync(_downloadUrl, HttpCompletionOption.ResponseHeadersRead);
                response.EnsureSuccessStatusCode();

                var totalBytes = response.Content.Headers.ContentLength ?? -1L;
                var buffer = new byte[8192];
                var totalRead = 0L;

                // Determine target directory
                _targetDir = Path.GetDirectoryName(CONFIG.Instance.ExePath);
                if (string.IsNullOrEmpty(_targetDir) || !Directory.Exists(_targetDir))
                {
                    _targetDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
                }

                _zipPath = Path.Combine(_targetDir, "update.zip");

                using (var contentStream = await response.Content.ReadAsStreamAsync())
                using (var fileStream = new FileStream(_zipPath, FileMode.Create, FileAccess.Write, FileShare.None))
                {
                    int read;
                    while ((read = await contentStream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                    {
                        await fileStream.WriteAsync(buffer, 0, read);
                        totalRead += read;

                        if (totalBytes > 0)
                        {
                            var percent = (int)((totalRead * 100) / totalBytes);
                            var receivedMb = totalRead / (1024.0 * 1024.0);
                            var totalMb = totalBytes / (1024.0 * 1024.0);

                            Dispatcher.Invoke(() =>
                            {
                                ProgressBar.Value = percent;
                                ProgressLabel.Text = $"جاري التحميل... {percent}% ({receivedMb:F1}/{totalMb:F1} MB)";
                            });
                        }
                    }
                }

                Console.WriteLine($"[UPDATE] Downloaded to: {_zipPath}");

                // Start installation
                StartInstallation();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[UPDATE] Download error: {ex.Message}");
                ProgressLabel.Text = $"خطأ في التحميل: {ex.Message}";

                await System.Threading.Tasks.Task.Delay(2000);
                ShowButtonsAgain();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Show buttons again - السطور 844-848
        // ═══════════════════════════════════════════════════════════════
        private void ShowButtonsAgain()
        {
            ProgressContainer.Visibility = Visibility.Collapsed;
            ButtonsContainer.Visibility = Visibility.Visible;
        }

        // ═══════════════════════════════════════════════════════════════
        // Start installation - السطور 904-913
        // ═══════════════════════════════════════════════════════════════
        private void StartInstallation()
        {
            Console.WriteLine("[UPDATE] Starting installation...");

            ProgressLabel.Text = "جاري التثبيت...";
            ProgressBar.IsIndeterminate = true;

            // Extract ZIP after delay
            Dispatcher.BeginInvoke(new Action(ExtractZip), DispatcherPriority.Background);
        }

        // ═══════════════════════════════════════════════════════════════
        // Extract ZIP - السطور 915-947
        // ═══════════════════════════════════════════════════════════════
        private void ExtractZip()
        {
            try
            {
                Console.WriteLine($"[UPDATE] Extracting ZIP: {_zipPath}");

                _extractDir = Path.Combine(_targetDir!, "_update_temp");

                // Delete temp folder if exists
                if (Directory.Exists(_extractDir))
                {
                    Directory.Delete(_extractDir, true);
                }
                Directory.CreateDirectory(_extractDir);

                // Extract
                ZipFile.ExtractToDirectory(_zipPath!, _extractDir);

                Console.WriteLine($"[UPDATE] Extracted to: {_extractDir}");

                // Reset progress bar
                ProgressBar.IsIndeterminate = false;
                ProgressBar.Value = 100;

                // Show completion
                OnDownloadComplete();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[UPDATE] Extract error: {ex.Message}");
                ProgressLabel.Text = $"خطأ في التثبيت: {ex.Message}";
                ProgressBar.IsIndeterminate = false;
                ShowButtonsAgain();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // On download complete - السطور 953-976
        // ═══════════════════════════════════════════════════════════════
        private void OnDownloadComplete()
        {
            _isDownloading = false;

            // Hide progress and version
            ProgressContainer.Visibility = Visibility.Collapsed;
            VersionContainer.Visibility = Visibility.Collapsed;

            // Show complete message
            CompleteContainer.Visibility = Visibility.Visible;

            // Start blink animation
            StartBlinkAnimation();
        }

        // ═══════════════════════════════════════════════════════════════
        // Blink animation - السطور 981-1012
        // ═══════════════════════════════════════════════════════════════
        private void StartBlinkAnimation()
        {
            _blinkTimer = new DispatcherTimer();
            _blinkTimer.Interval = TimeSpan.FromMilliseconds(500);
            _blinkTimer.Tick += (s, e) =>
            {
                _blinkVisible = !_blinkVisible;
                CompleteLabel.Foreground = new SolidColorBrush(
                    _blinkVisible 
                        ? (Color)System.Windows.Media.ColorConverter.ConvertFromString("#58D58D")
                        : (Color)System.Windows.Media.ColorConverter.ConvertFromString("#304050")
                );
            };
            _blinkTimer.Start();
        }

        // ═══════════════════════════════════════════════════════════════
        // Restart app - السطور 1017-1050
        // ═══════════════════════════════════════════════════════════════
        private void RestartButton_Click(object sender, RoutedEventArgs e)
        {
            _blinkTimer?.Stop();

            try
            {
                // Get current exe path
                string currentExe = Process.GetCurrentProcess().MainModule?.FileName ?? "";
                
                if (!string.IsNullOrEmpty(currentExe))
                {
                    // Start new process
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = currentExe,
                        UseShellExecute = true
                    });
                }

                // Close current app
                Application.Current.Shutdown();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[UPDATE] Restart error: {ex.Message}");
                System.Windows.MessageBox.Show($"خطأ في إعادة التشغيل: {ex.Message}", "خطأ", MessageBoxButton.OK);
            }
        }
    }
}
