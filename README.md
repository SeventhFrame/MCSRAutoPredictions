# MCSR Auto Predictions

This is a basic Windows local webapp for automatically running Twitch predictions for MCSR matches.

## Running the app

To run, download `MCSRAutoPredictions.exe` from the Releases section of this repo, then run the .exe on Windows.

You may get a security warning. Run the app anyway, and/or verify the contents of the .exe using the instructions below if you want to be certain it's safe.

A console window will open and the app will open your default browser. The app will run on a local web server (i.e., your PC) so your browser can open the app. No data runs to any external servers/clients apart from Twitch, the app itself will run locally and store any data on your system.

The app works by getting a token from twitch, storing it on your PC, using that token to run predictions via the Twitch API. It then polls public MCSR match history using your MCSR username, which you supply. Whenever you finish a match in MCSR, the app will check whether you won and then resolve the prediction. Then it'll start the next prediction.

To finish using the app, click 'Stop Bot'. This will cancel the latest ongoing prediction.

## Verifying the app contents

If you'd like to verify that the .exe matches the contents of this git repository:

Get the hash:

```powershell
Get-FileHash .\MCSRAutoPredictions.exe -Algorithm SHA256
```

Compare the `Hash` value with the published hash. Same hash = same file and therefore matches the contents of this git repo.

Current SHA-256 hash: 5A272F5760830BC17D4DE32B840BF9F62BF0ADD5E289EE997DF4B7AA5FCD99CB

## Build

If you'd like to build the project yourself (windows only):

- Install Python 3.12.

- Open PowerShell in this folder.

Run:

```powershell
.\build-windows.ps1
```

The file will be here:

```text
MCSRAutoPredictions.exe
```


