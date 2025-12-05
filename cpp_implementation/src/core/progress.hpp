#pragma once

#include <string>
#include <iostream>
#include <iomanip>
#include <chrono>

using namespace std;

// ANSI color codes
namespace Color {
    const string RESET = "\033[0m";
    const string RED = "\033[31m";
    const string GREEN = "\033[32m";
    const string YELLOW = "\033[33m";
    const string BLUE = "\033[34m";
    const string MAGENTA = "\033[35m";
    const string CYAN = "\033[36m";
    const string WHITE = "\033[37m";
    const string BOLD = "\033[1m";
    const string DIM = "\033[2m";
}

// ASCII symbols (no Unicode for compatibility)
namespace Symbol {
    const string CHECK = "[OK]";
    const string CROSS = "[X]";
    const string ARROW = "->";
    const string BULLET = "*";
    const string PACKAGE = "";
    const string SEARCH = "";
    const string DOWNLOAD = "";
    const string INSTALL = "";
    const string TRASH = "";
    const string CLOCK = "";
    const string WARN = "[!]";
    const string INFO = "[i]";
}

class ProgressBar {
public:
    ProgressBar(int total, const string& prefix = "", int width = 40)
        : total(total), current(0), prefix(prefix), width(width) {
        start_time = chrono::steady_clock::now();
    }
    
    void update(int value) {
        current = value;
        render();
    }
    
    void increment() {
        current++;
        render();
    }
    
    void finish() {
        current = total;
        render();
        cout << endl;
    }
    
    void setPrefix(const string& p) {
        prefix = p;
    }
    
private:
    int total;
    int current;
    string prefix;
    int width;
    chrono::steady_clock::time_point start_time;
    
    void render() {
        float progress = (total > 0) ? (float)current / total : 0;
        int filled = (int)(progress * width);
        
        // Calculate elapsed time
        auto now = chrono::steady_clock::now();
        auto elapsed = chrono::duration_cast<chrono::seconds>(now - start_time).count();
        
        // build progress bar
        string bar = "";
        for (int i = 0; i < width; i++) {
            if (i < filled) {
                bar += "=";
            } else if (i == filled) {
                bar += ">";
            } else {
                bar += " ";
            }
        }
        
        cout << "\r" << Color::CYAN << prefix << Color::RESET << " ";
        cout << Color::BLUE << bar << Color::RESET << " ";
        cout << Color::BOLD << setw(3) << (int)(progress * 100) << "%" << Color::RESET;
        cout << Color::DIM << " (" << current << "/" << total << ")";
        
        if (elapsed > 0 && current > 0) {
            int eta = (int)((elapsed * (total - current)) / current);
            cout << " ETA: " << eta << "s";
        }
        
        cout << Color::RESET << "   " << flush;
    }
};

class Spinner {
public:
    Spinner(const string& message = "Loading")
        : message(message), running(false), frame(0) {}
    
    void start() {
        running = true;
        render();
    }
    
    void update(const string& msg) {
        message = msg;
        frame++;
        render();
    }
    
    void stop(bool success = true) {
        running = false;
        cout << "\r";
        if (success) {
            cout << Color::GREEN << Symbol::CHECK << Color::RESET << " " << message;
        } else {
            cout << Color::RED << Symbol::CROSS << Color::RESET << " " << message;
        }
        cout << string(20, ' ') << endl;
    }
    
private:
    string message;
    bool running;
    int frame;
    const string frames[8] = {"|", "/", "-", "\\", "|", "/", "-", "\\"};
    
    void render() {
        cout << "\r" << Color::CYAN << frames[frame % 8] << Color::RESET 
             << " " << message << "   " << flush;
    }
};

// Formatted output helpers
class Output {
public:
    static void header(const string& text) {
        cout << endl;
        cout << Color::BOLD << Color::CYAN << "+-- " << text << " ";
        for (size_t i = 0; i < 50 - text.length(); i++) cout << "-";
        cout << "+" << Color::RESET << endl;
    }
    
    static void footer() {
        cout << Color::CYAN << "+";
        for (int i = 0; i < 52; i++) cout << "-";
        cout << "+" << Color::RESET << endl;
        cout << endl;
    }
    
    static void section(const string& title) {
        cout << endl;
        cout << Color::BOLD << Color::BLUE << Symbol::ARROW << " " << title << Color::RESET << endl;
    }
    
    static void success(const string& message) {
        cout << Color::GREEN << Symbol::CHECK << Color::RESET << " " << message << endl;
    }
    
    static void error(const string& message) {
        cout << Color::RED << Symbol::CROSS << Color::RESET << " " << message << endl;
    }
    
    static void warning(const string& message) {
        cout << Color::YELLOW << Symbol::WARN << Color::RESET << " " << message << endl;
    }
    
    static void info(const string& message) {
        cout << Color::BLUE << Symbol::INFO << Color::RESET << " " << message << endl;
    }
    
    static void package(const string& name, const string& version, const string& status = "") {
        cout << "  " << Color::CYAN << Symbol::BULLET << Color::RESET << " ";
        cout << Color::BOLD << name << Color::RESET;
        cout << Color::DIM << " " << version << Color::RESET;
        if (!status.empty()) {
            cout << " " << status;
        }
        cout << endl;
    }
    
    static void packageInstalled(const string& name, const string& version) {
        cout << "  " << Color::GREEN << Symbol::CHECK << Color::RESET << " ";
        cout << Color::BOLD << name << Color::RESET;
        cout << Color::DIM << " " << version << Color::RESET;
        cout << Color::GREEN << " installed" << Color::RESET << endl;
    }
    
    static void packageRemoved(const string& name) {
        cout << "  " << Color::YELLOW << Symbol::TRASH << Color::RESET << " ";
        cout << Color::BOLD << name << Color::RESET;
        cout << Color::YELLOW << " removed" << Color::RESET << endl;
    }
    
    static void packageFailed(const string& name, const string& reason = "") {
        cout << "  " << Color::RED << Symbol::CROSS << Color::RESET << " ";
        cout << Color::BOLD << name << Color::RESET;
        cout << Color::RED << " failed" << Color::RESET;
        if (!reason.empty()) {
            cout << Color::DIM << " (" << reason << ")" << Color::RESET;
        }
        cout << endl;
    }
    
    static void stats(int resolved, int installed, float time_seconds) {
        cout << endl;
        cout << Color::DIM << "---------------------------------------" << Color::RESET << endl;
        cout << Color::BOLD << resolved << Color::RESET 
             << " packages resolved, ";
        cout << Color::GREEN << installed << " installed" << Color::RESET << " in ";
        cout << Color::CYAN << fixed << setprecision(1) << time_seconds << "s" << Color::RESET << endl;
    }
    
    static void table(const vector<vector<string>>& rows, const vector<string>& headers) {
        if (rows.empty()) return;
        
        // Calculate column widths
        vector<int> widths(headers.size(), 0);
        for (size_t i = 0; i < headers.size(); i++) {
            widths[i] = headers[i].length();
        }
        for (const auto& row : rows) {
            for (size_t i = 0; i < row.size() && i < widths.size(); i++) {
                widths[i] = max(widths[i], (int)row[i].length());
            }
        }
        
        // Print header
        cout << Color::BOLD;
        for (size_t i = 0; i < headers.size(); i++) {
            cout << left << setw(widths[i] + 2) << headers[i];
        }
        cout << Color::RESET << endl;
        
        // Print separator
        cout << Color::DIM;
        for (size_t i = 0; i < headers.size(); i++) {
            cout << string(widths[i] + 2, '-');
        }
        cout << Color::RESET << endl;
        
        // Print rows
        for (const auto& row : rows) {
            for (size_t i = 0; i < row.size(); i++) {
                cout << left << setw(widths[i] + 2) << row[i];
            }
            cout << endl;
        }
    }
};

