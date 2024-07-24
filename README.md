## DWM Colorization Calculator
Converts `HSB` color and control panel color intensity slider or just `ARGB` color to the `DWMCOLORIZATIONPARAMETERS` structure used by `DwmSetColorizationParameters`.  

You can read the code to understand how the Windows 7 Control Panel converts the values of several sliders into relevant DWM registry items.

### Details
Windows 7 Control Panel colors are actually in HSB format, and the color intensity slider actually controls the alpha value of the converted `CColorizationColor` structure which is a `DWORD` stored in `ARGB` format. 

When the user moves the sliders, the control panel reads the values of those sliders and performs a color format conversion. For some strange reasons, the value of the slider for color intensity is limited to `0x0D(13)` to `0xD9(217)`. 

Windows 10 only retains the last bit of calculations regarding color balance, however `ColorizationAfterglowBalance` is hardcoded to 10 and `ColorizationBlurBalance` is hardcoded to 1. Inside UxTheme.dll, new immersive color-related interfaces and functions have been introduced, which internally check if the calculated result of current color matches the value in the registry, and override the registry value if it doesn't, which is why [`Colorization*Balance` is often reset to its default value](https://github.com/ALTaleX531/OpenGlass/issues/4).