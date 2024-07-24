class dwm_colorization_parameters: pass
class colorization_color: pass

class hsb:
    # hue: 0..360
    # saturation: 0..1
    # brightness: 0..1
    def __init__(self, hue:float, saturation:float, brightness:float) -> None:
        self.hue = hue
        self.saturation = saturation
        self.brightness = brightness
    def __str__(self) -> str:
        return f'[hue:{self.hue:.2f}, saturation:{self.saturation:.2f}, brightness:{self.brightness:.2f}]'
class argb(int):
    def __str__(self) -> str: return hex(self)
    def get_a(self) -> int: return (self & 0xFF000000) >> 24
    def get_r(self) -> int: return (self & 0x00FF0000) >> 16
    def get_g(self) -> int: return (self & 0x0000FF00) >> 8
    def get_b(self) -> int: return (self & 0x000000FF) >> 0
    def from_argb_channel(a:float, r:float, g:float, b:float):
        return argb(
            ((int(a * 255.0 + 0.5) & 0xFF) << 24) | \
            ((int(r * 255.0 + 0.5) & 0xFF) << 16) | \
            ((int(g * 255.0 + 0.5) & 0xFF) << 8) | \
            ((int(b * 255.0 + 0.5) & 0xFF) << 0)
        )

class colorization_color(argb):
    # themecpl.dll!CColorizationColor::CColorizationColor
    def from_hsb(color:hsb, intensity:float) -> colorization_color:
        if color.saturation == 0.0:
            r = g = b = color.brightness
        
        value = color.hue / 60.0
        difference = value - float(int(value))
        
        match color.hue:
            case hue if 0.0 < hue <= 60.0:
                g = (1.0 - (1.0 - difference) * color.saturation) * color.brightness
                b = (1.0 - color.saturation) * color.brightness
                r = color.brightness
            case hue if 60.0 < hue <= 120.0:
                r = (1.0 - difference * color.saturation) * color.brightness
                g = color.brightness
                b = (1.0 - color.saturation) * color.brightness
            case hue if 120.0 < hue <= 180.0:
                r = (1.0 - color.saturation) * color.brightness
                g = color.brightness
                b = (1.0 - (1.0 - difference) * color.saturation) * color.brightness
            case hue if 180.0 < hue <= 240.0:
                r = (1.0 - color.saturation) * color.brightness
                g = (1.0 - difference * color.saturation) * color.brightness
                b = color.brightness
            case hue if 240.0 < hue <= 300.0:
                r = (1.0 - (1.0 - difference) * color.saturation) * color.brightness
                g = (1.0 - color.saturation) * color.brightness
                b = color.brightness
            case hue if 300.0 < hue <= 360.0:
                g = (1.0 - color.saturation) * color.brightness
                b = (1.0 - difference * color.saturation) * color.brightness
                r = color.brightness
            case _:
                pass
            
        return colorization_color(
            argb.from_argb_channel(
                intensity,
                r,
                g,
                b
            )
        )
    
    # themecpl.dll!CColorCplPage::UpdateSlidersToReflectColor
    # The range for the slider is about [10%, 85%], normally you can't make it bigger or smaller
    def get_intensity(self) -> float:
        return float(self.get_a()) / 255.0
    # themecpl.dll!CColorCplPage::UpdateSlidersToReflectColor
    def get_hsb_color(self) -> hsb:
        r = float(self.get_r()) / 255.0
        g = float(self.get_g()) / 255.0
        b = float(self.get_b()) / 255.0
        
        brightness = max(r, g, b)
        darkness = min(r, g, b)
        
        range_value = brightness - darkness
        if brightness == 0.0 or range_value == 0.0:
            saturation = 0.0
            value = 0.0
        else:
            saturation = range_value / brightness
            if r == brightness:
                value = (g - b) / range_value
            elif g == brightness:
                value = (b - r) / range_value + 2.0
            else:
                value = (r - g) / range_value + 4.0
        hue = value * 60.0
        hue += 360.0 if hue < 0.0 else 0.0
        
        return hsb(
            hue, 
            saturation, 
            brightness
        )
        
    
    # themecpl.dll!CColorCplPage::SetDwmColorizationColor
    def to_dwm_colorization_parameters(self, opaque:bool = False) -> dwm_colorization_parameters:
        balance = int((float((self >> 24) & 0xFF) / 255.0 - 0.1) / 0.75 * 100.0 + 10.0)
        
        params = dwm_colorization_parameters(
            color = self,
            afterglow = self,
            glass_reflection_intensity = 50,
            opaque_blend = opaque
        )
        if opaque:
            params.afterglow_balance = 10
            params.color_balance = balance - params.afterglow_balance
            params.blur_balance = 100 - balance
            return params
            
        if balance < 50:
            params.color_balance = 5
            params.blur_balance = 100 - balance
            params.afterglow_balance = (100 - params.color_balance) - params.blur_balance
            return params
            
        if balance >= 95:
            params.afterglow_balance = 0
            params.color_balance = balance - 25
            params.blur_balance = 100 - params.color_balance
            return params
            
        params.afterglow_balance = 95 - balance
        params.blur_balance = 50 - ((balance - 50) >> 1)
        params.color_balance = 100 - params.afterglow_balance - params.blur_balance
        return params

# DWMCOLORIZATIONPARAMETERS
class dwm_colorization_parameters:
    # default colorization parameters for Windows 7 Sky
    def __init__(
        self,
        color:argb = 0x6b74b8fc,                #.0 a is actually ignored in the shader
        afterglow:argb = 0x6b74b8fc,            #.1 a is actually ignored in the shader
        color_balance:int = 8,                  #.2 0..100
        afterglow_balance:int = 43,             #.3 0..100
        blur_balance:int = 49,                  #.4 0..100
        glass_reflection_intensity:int = 50,    #.5 0..100
        opaque_blend:bool = False               #.6
    ) -> None:
        self.color = color
        self.afterglow = afterglow
        self.color_balance = color_balance
        self.afterglow_balance = afterglow_balance
        self.blur_balance = blur_balance
        self.glass_reflection_intensity = glass_reflection_intensity
        self.opaque_blend = opaque_blend
    def __str__(self) -> str:
        return '[color:{}, afterglow:{}, color_balance:{}, afterglow_balance:{}, blur_balance:{}, glass_reflection_intensity:{}, opaque_blend:{}]'.format(
            hex(self.color),
            hex(self.afterglow),
            self.color_balance,
            self.afterglow_balance,
            self.blur_balance,
            self.glass_reflection_intensity,
            self.opaque_blend
        )
    
    # themecpl.dll!ConvertColorizationParametersToARGB
    def convert_colorization_parameters_to_argb(self) -> colorization_color:
        balance = 0
    
        if self.opaque_blend:
            balance = self.color_balance
        elif self.blur_balance < 50:
            if self.blur_balance <= 23:
                balance = self.color_balance + 25
            else:
                balance = 95 - self.afterglow_balance
        else:
            balance = 100 - self.blur_balance
        
        return self.color & 0xFFFFFF | ((int((float(balance - 10) * 0.75 / 100.0 + 0.1) * 255.0 + 0.5) & 0xFF) << 24)
    
    # themecpl.dll!CColorCplPage::Setup
    # used by theme control panel
    def to_colorization_color(self) -> colorization_color:
        argb_color = 0
        
        if (self.color & 0xFF000000) == 0xFF000000:
            argb_color = self.convert_colorization_parameters_to_argb(self)
        else:
            argb_color = self.color
            
        return colorization_color(argb_color)
    
    # udwm.dll!DwmpCalculateColorizationColor
    # used by WM_DWMCOLORIZATIONCOLORCHANGED and DwmGetColorizationColor
    # 
    # https://stackoverflow.com/questions/3560890/vista-7-how-to-get-glass-color
    # It's almost unusable, I keep it simply because its implementation exists inside udwm.dll from Windows 7.
    def calculate_dwm_color(self) -> colorization_color:
        afterglow_balance = float(self.afterglow_balance) / 100.0
        color_balance = float(self.color_balance) / 100.0
        
        color_r = float(self.color.get_r()) / 255.0
        color_g = float(self.color.get_g()) / 255.0
        color_b = float(self.color.get_b()) / 255.0
        
        afterglow_r = float(self.afterglow.get_r()) / 255.0
        afterglow_g = float(self.afterglow.get_g()) / 255.0
        afterglow_b = float(self.afterglow.get_b()) / 255.0
        
        result_a = max(0.0, (1.0 - afterglow_balance) - (float(self.blur_balance) / 100.0))
        brightness = (color_g * 0.7152 + color_r * 0.2126 + color_b * 0.0722) * afterglow_balance * color_balance
        
        result_r = afterglow_r * brightness + color_r * color_balance
        result_g = afterglow_g * brightness + color_g * color_balance
        result_b = afterglow_b * brightness + color_b * color_balance
        
        return colorization_color(
            argb.from_argb_channel(
                result_a,
                result_r,
                result_g,
                result_b
            )
        )
        
colorization_params = dwm_colorization_parameters()
color = colorization_params.to_colorization_color()
hsb_color = color.get_hsb_color()
intensity = color.get_intensity()
params_from_color = color.to_dwm_colorization_parameters(colorization_params.opaque_blend)
color_from_hsb = colorization_color.from_hsb(hsb_color, intensity)

print('DWM Colorization Calculator v1.0.0 - Converts HSB color and control panel color intensity slider or just ARGB color to the DWMCOLORIZATIONPARAMETERS structure used by DwmSetColorizationParameters.')
print('This demo application was written by @ALTaleX based on the disassembled code of themecpl.dll in Windows 7, thus its results are the most accurate and undoubted.')
print()

print("Here's a sample (Windows 7 Sky colorization parameters): ")
print(f'colorization_params: {colorization_params}')
print(f'colorization_params.to_colorization_color(): {color}')
print(f'colorization_color.from_hsb(color.get_hsb_color(), color.get_intensity()): {color_from_hsb}')
print()
print(f'colorization_params.to_colorization_color().get_hsb_color(): {hsb_color}')
print(f'colorization_params.to_colorization_color().get_intensity(): {intensity:.2f}')
print()
print(f'colorization_params.to_colorization_color().to_dwm_colorization_parameters(): {params_from_color}')
print(f'colorization_params.to_colorization_color().to_dwm_colorization_parameters.to_colorization_color(): {params_from_color.to_colorization_color()}')
print()

print('Now is your turn! (Ctrl+Break to quit)')
while True: print('colorization_parameters: ', colorization_color(input('Input glass color hex (ARGB format): '), 16).to_dwm_colorization_parameters())