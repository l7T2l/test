// ═══════════════════════════════════════════════════════════════════════════════
// Config.cs - مدير الإعدادات
// المقابل لـ: main.py السطور 40-94 (class ConfigManager)
// تحويل سطر بسطر - كل قيمة افتراضية مطابقة للأصل
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Collections.Generic;

namespace SmartKeyboard
{
    /// <summary>
    /// class ConfigManager: - السطر 40
    /// مدير إعدادات البرنامج
    /// </summary>
    public class ConfigManager
    {
        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - السطور 42-68
        // ═══════════════════════════════════════════════════════════════

        // السطر 42: self.config_file = "config.json"
        private readonly string _configFile = "config.json";

        // السطور 43-68: self.defaults = { ... }
        private readonly AppConfig _defaults = new AppConfig
        {
            // السطر 44: "x": 586, "y": 418, "w": 468, "h": 90
            X = 586,
            Y = 418,
            W = 468,
            H = 90,

            // السطر 45: "bg_color": "#000000", "text_color": "#FFFF00"
            BgColor = "#000000",
            TextColor = "#FFFF00",

            // السطر 46: "bg_opacity": 200, "text_opacity": 255
            BgOpacity = 200,
            TextOpacity = 255,

            // السطر 47: "settings_opacity": 230
            SettingsOpacity = 230,

            // السطر 48: "font_size": 20
            FontSize = 20,

            // السطر 49: "first_line_end": 0
            FirstLineEnd = 0,

            // السطر 50: "hotkey": "insert"
            Hotkey = "insert",

            // السطر 51: "game_click_x": -1, "game_click_y": -1
            GameClickX = -1,
            GameClickY = -1,

            // السطر 52: "game_name": ""
            GameName = "",

            // السطر 53: "settings_x": -1, "settings_y": -1
            SettingsX = -1,
            SettingsY = -1,

            // السطر 54: "pinned_mode": False
            PinnedMode = false,

            // السطر 55: "send_mode": "enter"
            SendMode = "enter",

            // السطر 56: "favorite_colors": ["", "", "", "", "", ""]
            FavoriteColors = new List<string> { "", "", "", "", "", "" },

            // السطر 57: "exe_path": ""
            ExePath = "",

            // السطور 61-67: إعدادات كشف الشات
            ChatOpenColor = "",        // السطر 61
            ChatClosedColor = "",      // السطر 62
            ChatDetectX = -1,          // السطر 63
            ChatDetectY = -1,          // السطر 64
            ChatDetectEnabled = false, // السطر 65
            ChatOpenEnters = 0,        // السطر 66
            ChatClosedEnters = 1       // السطر 67
        };

        // السطر 69: self.config = self.load_config()
        private AppConfig _config;

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - السطر 41: def __init__(self)
        // ═══════════════════════════════════════════════════════════════
        public ConfigManager()
        {
            _config = LoadConfig();
        }

        // ═══════════════════════════════════════════════════════════════
        // load_config - السطور 71-78
        // ═══════════════════════════════════════════════════════════════
        private AppConfig LoadConfig()
        {
            // السطر 72: if os.path.exists(self.config_file)
            if (File.Exists(_configFile))
            {
                try
                {
                    // السطور 74-75
                    string json = File.ReadAllText(_configFile);
                    var loaded = JsonSerializer.Deserialize<AppConfig>(json);
                    if (loaded != null)
                    {
                        // Merge with defaults
                        return MergeWithDefaults(loaded);
                    }
                }
                catch
                {
                    // السطور 76-77: except: pass
                }
            }
            // السطر 78: return self.defaults.copy()
            return CloneConfig(_defaults);
        }

        // ═══════════════════════════════════════════════════════════════
        // save_config - السطور 80-85
        // ═══════════════════════════════════════════════════════════════
        public void SaveConfig()
        {
            try
            {
                // السطور 82-83
                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(_config, options);
                File.WriteAllText(_configFile, json);
            }
            catch (Exception e)
            {
                // السطور 84-85
                Console.WriteLine($"Config Save Error: {e.Message}");
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // get - السطور 87-88
        // ═══════════════════════════════════════════════════════════════
        public T Get<T>(string key)
        {
            var property = typeof(AppConfig).GetProperty(key);
            if (property != null)
            {
                return (T)(property.GetValue(_config) ?? property.GetValue(_defaults)!);
            }
            throw new ArgumentException($"Unknown config key: {key}");
        }

        // Overload for common types
        public int GetInt(string key) => Get<int>(key);
        public string GetString(string key) => Get<string>(key) ?? "";
        public bool GetBool(string key) => Get<bool>(key);

        // ═══════════════════════════════════════════════════════════════
        // set - السطور 90-92
        // ═══════════════════════════════════════════════════════════════
        public void Set(string key, object value)
        {
            // السطور 91-92
            var property = typeof(AppConfig).GetProperty(key);
            if (property != null)
            {
                property.SetValue(_config, value);
                SaveConfig();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Helper methods
        // ═══════════════════════════════════════════════════════════════
        private AppConfig MergeWithDefaults(AppConfig loaded)
        {
            // ينسخ القيم الافتراضية ثم يدمج فوقها القيم المحملة
            var result = CloneConfig(_defaults);

            foreach (var prop in typeof(AppConfig).GetProperties())
            {
                var loadedValue = prop.GetValue(loaded);
                if (loadedValue != null)
                {
                    prop.SetValue(result, loadedValue);
                }
            }

            return result;
        }

        private static AppConfig CloneConfig(AppConfig source)
        {
            return new AppConfig
            {
                X = source.X,
                Y = source.Y,
                W = source.W,
                H = source.H,
                BgColor = source.BgColor,
                TextColor = source.TextColor,
                BgOpacity = source.BgOpacity,
                TextOpacity = source.TextOpacity,
                SettingsOpacity = source.SettingsOpacity,
                FontSize = source.FontSize,
                FirstLineEnd = source.FirstLineEnd,
                Hotkey = source.Hotkey,
                GameClickX = source.GameClickX,
                GameClickY = source.GameClickY,
                GameName = source.GameName,
                SettingsX = source.SettingsX,
                SettingsY = source.SettingsY,
                PinnedMode = source.PinnedMode,
                SendMode = source.SendMode,
                FavoriteColors = new List<string>(source.FavoriteColors),
                ExePath = source.ExePath,
                ChatOpenColor = source.ChatOpenColor,
                ChatClosedColor = source.ChatClosedColor,
                ChatDetectX = source.ChatDetectX,
                ChatDetectY = source.ChatDetectY,
                ChatDetectEnabled = source.ChatDetectEnabled,
                ChatOpenEnters = source.ChatOpenEnters,
                ChatClosedEnters = source.ChatClosedEnters
            };
        }

        // ═══════════════════════════════════════════════════════════════
        // Direct property accessors (للتسهيل)
        // ═══════════════════════════════════════════════════════════════
        public int X { get => _config.X; set { _config.X = value; SaveConfig(); } }
        public int Y { get => _config.Y; set { _config.Y = value; SaveConfig(); } }
        public int W { get => _config.W; set { _config.W = value; SaveConfig(); } }
        public int H { get => _config.H; set { _config.H = value; SaveConfig(); } }
        public string BgColor { get => _config.BgColor; set { _config.BgColor = value; SaveConfig(); } }
        public string TextColor { get => _config.TextColor; set { _config.TextColor = value; SaveConfig(); } }
        public int BgOpacity { get => _config.BgOpacity; set { _config.BgOpacity = value; SaveConfig(); } }
        public int TextOpacity { get => _config.TextOpacity; set { _config.TextOpacity = value; SaveConfig(); } }
        public int SettingsOpacity { get => _config.SettingsOpacity; set { _config.SettingsOpacity = value; SaveConfig(); } }
        public int FontSize { get => _config.FontSize; set { _config.FontSize = value; SaveConfig(); } }
        public int FirstLineEnd { get => _config.FirstLineEnd; set { _config.FirstLineEnd = value; SaveConfig(); } }
        public string Hotkey { get => _config.Hotkey; set { _config.Hotkey = value; SaveConfig(); } }
        public int GameClickX { get => _config.GameClickX; set { _config.GameClickX = value; SaveConfig(); } }
        public int GameClickY { get => _config.GameClickY; set { _config.GameClickY = value; SaveConfig(); } }
        public string GameName { get => _config.GameName; set { _config.GameName = value; SaveConfig(); } }
        public int SettingsX { get => _config.SettingsX; set { _config.SettingsX = value; SaveConfig(); } }
        public int SettingsY { get => _config.SettingsY; set { _config.SettingsY = value; SaveConfig(); } }
        public bool PinnedMode { get => _config.PinnedMode; set { _config.PinnedMode = value; SaveConfig(); } }
        public string SendMode { get => _config.SendMode; set { _config.SendMode = value; SaveConfig(); } }
        public List<string> FavoriteColors { get => _config.FavoriteColors; set { _config.FavoriteColors = value; SaveConfig(); } }
        public string ExePath { get => _config.ExePath; set { _config.ExePath = value; SaveConfig(); } }
        public string ChatOpenColor { get => _config.ChatOpenColor; set { _config.ChatOpenColor = value; SaveConfig(); } }
        public string ChatClosedColor { get => _config.ChatClosedColor; set { _config.ChatClosedColor = value; SaveConfig(); } }
        public int ChatDetectX { get => _config.ChatDetectX; set { _config.ChatDetectX = value; SaveConfig(); } }
        public int ChatDetectY { get => _config.ChatDetectY; set { _config.ChatDetectY = value; SaveConfig(); } }
        public bool ChatDetectEnabled { get => _config.ChatDetectEnabled; set { _config.ChatDetectEnabled = value; SaveConfig(); } }
        public int ChatOpenEnters { get => _config.ChatOpenEnters; set { _config.ChatOpenEnters = value; SaveConfig(); } }
        public int ChatClosedEnters { get => _config.ChatClosedEnters; set { _config.ChatClosedEnters = value; SaveConfig(); } }
    }

    /// <summary>
    /// كائن الإعدادات - مطابق لـ defaults dict في السطور 43-68
    /// </summary>
    public class AppConfig
    {
        // السطر 44
        [JsonPropertyName("x")] public int X { get; set; }
        [JsonPropertyName("y")] public int Y { get; set; }
        [JsonPropertyName("w")] public int W { get; set; }
        [JsonPropertyName("h")] public int H { get; set; }

        // السطر 45
        [JsonPropertyName("bg_color")] public string BgColor { get; set; } = "";
        [JsonPropertyName("text_color")] public string TextColor { get; set; } = "";

        // السطر 46
        [JsonPropertyName("bg_opacity")] public int BgOpacity { get; set; }
        [JsonPropertyName("text_opacity")] public int TextOpacity { get; set; }

        // السطر 47
        [JsonPropertyName("settings_opacity")] public int SettingsOpacity { get; set; }

        // السطر 48
        [JsonPropertyName("font_size")] public int FontSize { get; set; }

        // السطر 49
        [JsonPropertyName("first_line_end")] public int FirstLineEnd { get; set; }

        // السطر 50
        [JsonPropertyName("hotkey")] public string Hotkey { get; set; } = "";

        // السطر 51
        [JsonPropertyName("game_click_x")] public int GameClickX { get; set; }
        [JsonPropertyName("game_click_y")] public int GameClickY { get; set; }

        // السطر 52
        [JsonPropertyName("game_name")] public string GameName { get; set; } = "";

        // السطر 53
        [JsonPropertyName("settings_x")] public int SettingsX { get; set; }
        [JsonPropertyName("settings_y")] public int SettingsY { get; set; }

        // السطر 54
        [JsonPropertyName("pinned_mode")] public bool PinnedMode { get; set; }

        // السطر 55
        [JsonPropertyName("send_mode")] public string SendMode { get; set; } = "";

        // السطر 56
        [JsonPropertyName("favorite_colors")] public List<string> FavoriteColors { get; set; } = new();

        // السطر 57
        [JsonPropertyName("exe_path")] public string ExePath { get; set; } = "";

        // السطور 61-67
        [JsonPropertyName("chat_open_color")] public string ChatOpenColor { get; set; } = "";
        [JsonPropertyName("chat_closed_color")] public string ChatClosedColor { get; set; } = "";
        [JsonPropertyName("chat_detect_x")] public int ChatDetectX { get; set; }
        [JsonPropertyName("chat_detect_y")] public int ChatDetectY { get; set; }
        [JsonPropertyName("chat_detect_enabled")] public bool ChatDetectEnabled { get; set; }
        [JsonPropertyName("chat_open_enters")] public int ChatOpenEnters { get; set; }
        [JsonPropertyName("chat_closed_enters")] public int ChatClosedEnters { get; set; }
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // السطر 94: CONFIG = ConfigManager()
    // Global instance
    // ═══════════════════════════════════════════════════════════════════════════════
    public static class CONFIG
    {
        private static ConfigManager? _instance;
        private static readonly object _lock = new object();

        public static ConfigManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    lock (_lock)
                    {
                        _instance ??= new ConfigManager();
                    }
                }
                return _instance;
            }
        }
    }
}
