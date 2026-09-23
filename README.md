# MCSR Auto Predictions

This is a basic local webapp on Windows for automatically running Twitch predictions for Minecraft Speedrunning (MCSR) Ranked matches.

## Download

Download the latest Windows build from GitHub Releases:

- [Latest release](https://github.com/SeventhFrame/MCSRAutoPredictions/releases/latest)

## Running the app

To run, download `MCSRAutoPredictions.exe` from the Releases section of this repo, then run the .exe on Windows.

You may get a security warning. Run the app anyway if you trust the author (i.e., me), or build the project yourself from the source code using the instructions in below section.

A console window will open and the app will open your default browser. The app will run on a local web server (i.e., your PC) so your browser can open the app. No data runs to any external servers/clients apart from Twitch, the app itself will run locally and store any data on your system.

The app works by getting a token from twitch, storing it on your PC, using that token to run predictions via the Twitch API. It then polls public MCSR match history using your MCSR username, which you supply. Whenever you finish a match in MCSR, the app will check whether you won and then resolve the prediction. Then it'll start the next prediction.

To finish using the app, click 'Stop Bot'. This will cancel the latest ongoing prediction.

The bot is hard-coded to run predictions with title "DO I WIN?" and outcomes "YES" or "NO" with a 120 second betting duration. In a future release you will be able to configure these in the webapp.

### Reliability / fixing errors

The bot should be fairly reliable, but it might become desynced with the actual state of your predictions in edge cases, e.g. if Twitch API times out or if you manually amend the predictions.

If this happens, simply stop the bot and end any predictions you have open if needed, then restart the bot. Should fix any problems.

## Build

If you'd like to build the project yourself on windows:

- Install Python 3.14

- Open PowerShell in this folder

Run:

```powershell
.\build-windows.ps1
```

The file will be created in directory as:

```text
MCSRAutoPredictions.exe
```


