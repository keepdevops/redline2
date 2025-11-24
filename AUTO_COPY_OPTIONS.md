# Auto-Copy Files to Container - Options

## Option 1: File Watcher (Real-Time) ⚡

Automatically copies files as they're downloaded to your Downloads folder.

```bash
./watch_and_copy.sh
```

**Features:**
- ✅ Monitors Downloads folder continuously
- ✅ Auto-copies new CSV/TXT/ZIP files
- ✅ Avoids duplicates
- ✅ Waits for downloads to complete
- ✅ Runs in background (Ctrl+C to stop)

**Install fswatch for real-time (recommended):**
```bash
brew install fswatch
```

**Without fswatch:**
- Falls back to polling mode (checks every 5 seconds)
- Still works, just not instant

## Option 2: Quick Copy (One-Liner) 🚀

Copy files immediately with a simple command.

```bash
# Copy all CSV/TXT/ZIP files
./quick_copy.sh

# Copy only AAPL files
./quick_copy.sh aapl

# Copy only GOOGL files
./quick_copy.sh googl

# Copy only Stooq files
./quick_copy.sh stooq
```

**Features:**
- ✅ Instant execution
- ✅ Pattern filtering
- ✅ No prompts, just runs
- ✅ Perfect for scripts/aliases

## Option 3: Interactive Batch (Enhanced) 📋

The original enhanced script with full selection options.

```bash
./copy_files_to_container.sh
```

**Features:**
- ✅ Numbered file list
- ✅ Select by number, range, or pattern
- ✅ Shows file sizes and dates
- ✅ Confirmation before copying

## Option 4: Alias for Quick Access

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Quick copy all files
alias copydata='~/redline/quick_copy.sh'

# Quick copy by ticker
alias copyaapl='~/redline/quick_copy.sh aapl'
alias copygoogl='~/redline/quick_copy.sh googl'
```

Then just run:
```bash
copydata      # Copy all files
copyaapl      # Copy AAPL files
```

## Option 5: Background Service (Advanced)

Run file watcher as a background service:

```bash
# Start watcher in background
nohup ./watch_and_copy.sh > /tmp/file_watcher.log 2>&1 &

# Check if running
ps aux | grep watch_and_copy

# Stop watcher
pkill -f watch_and_copy.sh
```

## Recommendation

**For daily use:** Use `watch_and_copy.sh` - set it and forget it!

**For quick one-time copies:** Use `quick_copy.sh` with pattern

**For selective batch:** Use `copy_files_to_container.sh`

