import sugarpidisplay.epd2in13 as epd2in13
import datetime
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from .trend import Trend


class Rect:
    def __init__(self,xy,size):
        self.xy = xy
        self.size = size

class EpaperDisplay:

    __epd = None
    __screenMode = ""
    __font = None
    __logger = None
    __hBlackImage = None
    __hRedImage = None
    __rectFull = Rect((0,0), (250,122))
    __rectBG = Rect((0,0), (125,70))
    __rectAge = Rect((0,70), (73,52))
    __rectTrend = Rect((73,70), (52,52))
    #__rectGraph = Rect(104,0,0,50)

    __imgBG = None
    __imgAge = None
    __imgTrend = None
    __dirty = False
    __allDirty = False

    __lastAge = 999
    __lastTrend = Trend.NONE

    __arrowImgSingle = None
    __arrowImgDouble = None


    def __init__(self, logger):
        self.__logger = logger
        self.__hBlackImage = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 298*126
        #self.__hRedImage = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 298*126

        self.__imgBG = Image.new('1', self.__rectBG.size, 255)
        self.__imgAge = Image.new('1', self.__rectAge.size, 255)
        self.__imgTrend = Image.new('1', self.__rectTrend.size, 255)
        self.__allImages = [self.__imgBG, self.__imgAge, self.__imgTrend]

        self.__fontMsg = ImageFont.truetype('/home/pi/SugarPiDisplay/sugarpidisplay/Inconsolata-Regular.ttf', 30)
        self.__fontBG = ImageFont.truetype('/home/pi/SugarPiDisplay/sugarpidisplay/Inconsolata-Regular.ttf', 74)
        self.__fontAge = ImageFont.truetype('/home/pi/SugarPiDisplay/sugarpidisplay/Inconsolata-Regular.ttf', 22)
        self.__fontTime = ImageFont.truetype('/home/pi/SugarPiDisplay/sugarpidisplay/Inconsolata-Regular.ttf', 18)

        self.__initTrendImages(self.__rectTrend.size)
        return None

    def open(self):
        self.__epd = epd2in13.EPD()
        #self.__create_custom_chars()
        return True

    def close(self):
        self.__epd.init(self.__epd.FULL_UPDATE)
        self.__epd.Clear(0xFF)
        self.__epd.sleep()
        self.__epd = None
        return True

    def __updateScreen(self):
        if (not self.__dirty):
            return
        self.__dirty = False
        if self.__screenMode == "egv":
            self.__wipeImage(self.__hBlackImage)
            self.__hBlackImage.paste(self.__imgBG, self.__rectBG.xy)
            self.__hBlackImage.paste(self.__imgAge, self.__rectAge.xy)
            self.__hBlackImage.paste(self.__imgTrend, self.__rectTrend.xy)
            if self.__allDirty:
                self.__epd.init(self.__epd.FULL_UPDATE)
                self.__allDirty = False
                self.__epd.display(self.__epd.getbuffer(self.__hBlackImage))
            else:
                self.__epd.init(self.__epd.PART_UPDATE)
                self.__epd.displayPartial(self.__epd.getbuffer(self.__hBlackImage))
            self.__epd.sleep()
        if self.__screenMode == "text":
            self.__epd.init(self.__epd.FULL_UPDATE)
            self.__epd.display(self.__epd.getbuffer(self.__hBlackImage))
            self.__epd.sleep()


    def __wipeImage(self, img):
        if (img is None):
            return
        draw = ImageDraw.Draw(img)
        draw.rectangle(((0,0), img.size), fill = (255) )
        #size = (img.size[0]-1, img.size[1]-1)
        #draw.rectangle(((0,0), size), outline = (0), fill = (255) )

    def clear(self):
        self.__epd.init(self.__epd.FULL_UPDATE)
        print("Clear...")
        self.__epd.Clear(0xFF)
        self.__epd.sleep()
        for img in self.__allImages:
            self.__wipeImage(img)
        self.__wipeImage(self.__hBlackImage)
        self.__screenMode = ""

    def show_centered(self, line0, line1):
        self.__setScreenModeToText()
        line0 = line0 if line0 is not None else ""
        line1 = line1 if line1 is not None else ""

        self.__logger.debug("Display: " + line0 + " || " + line1)
        print("Display: " + line0 + " || " + line1)

        self.__wipeImage(self.__hBlackImage)
        draw = ImageDraw.Draw(self.__hBlackImage)
        self.__drawText(draw, (5,5), line0, self.__fontMsg)
        self.__drawText(draw, (5,40), line1, self.__fontMsg)
        self.__dirty = True
        self.__updateScreen()


    def update(self, updates):
        self.__setScreenModeToEgv()
        if 'age' in updates.keys():
            self.__update_age(updates['age'])
        oldReading = 'oldreading' in updates.keys()
        if 'value' in updates.keys():
            self.__update_value(updates['value'], oldReading)
        if 'trend' in updates.keys():
            print ('calling update_trend')
            self.__update_trend(updates['trend'], oldReading)

        self.__updateScreen()

    def __update_value(self, value, isOldReading):
        valStr = "??" # this shouldn't happen
        if (value is not None):
            valStr = str(value)
        valStr = valStr.rjust(3)
        #print(valStr + "   " + str(mins))
        self.__wipeImage(self.__imgBG)
        drawBg = ImageDraw.Draw(self.__imgBG)
        textXY = (5, 8)

        textSize = self.__drawText(drawBg, textXY, valStr, self.__fontBG)
        if (isOldReading):
            drawBg.line((textXY[0], textXY[1] + textSize[1]//2, textXY[0]+textSize[0], textXY[1] + textSize[1]//2), fill = 0, width=2)
        self.__dirty = True
        self.__allDirty = True

    def __drawText(self, draw, xy, text, font):
        offset = font.getoffset(text)
        textSize = draw.textsize(text, font = font)
        textSize = (textSize[0] - offset[0], textSize[1] - offset[1])
        draw.text((xy[0]-offset[0], xy[1]-offset[1]), text, font = font, fill = 0)
        return textSize

    def __update_trend(self, trend, isOldReading):
        if (trend is None):
            trend = Trend.NONE
        if (isOldReading):
            trend = Trend.NONE
        if trend == self.__lastTrend:
            return
        self.__lastTrend = trend
        self.__wipeImage(self.__imgTrend)
        arrowImg = self.__get_trend_image(trend)
        if (arrowImg is not None):
            print("pasting arrow img")
            self.__imgTrend.paste(arrowImg, (0,0))
        self.__dirty = True
        self.__allDirty = True

    def __update_age(self, mins):
        self.__setScreenModeToEgv()
        #mins = (mins//2) * 2 # round to even number
        if (mins == self.__lastAge):
            return
        self.__lastAge = mins
        ageStr = "now"
        if (mins > 0):
            ageStr = str(mins) + "m"
        ageStr = ageStr.rjust(4)

        now = datetime.datetime.now().strftime('%I:%M%p')
        now = now.replace("AM", "a").replace("PM", "p")
        now = now.rjust(6)

        self.__wipeImage(self.__imgAge)
        draw = ImageDraw.Draw(self.__imgAge)
        self.__drawText(draw, (5,6), ageStr, self.__fontAge)
        self.__drawText(draw, (5,30), now, self.__fontTime)
        self.__dirty = True

    def updateAnimation(self):
        self.__setScreenModeToEgv()

    def __setScreenModeToEgv(self):
        if (not self.__screenMode == "egv"):
            self.__logger.debug("Display mode EGV")
            self.__screenMode = "egv"
            self.__lastAge = 999
            self.__lastTrend = Trend.NONE

    def __setScreenModeToText(self):
        if (not self.__screenMode == "text"):
            self.__logger.debug("Display mode Text")
            self.__screenMode = "text"


    def __initTrendImages(self, size):
        w = size[0]
        h = size[1]
        x2 = w - 1
        y2 = h - 1
        lw = 3
        self.__arrowImgSingle = Image.new('1', size, 255)
        draw = ImageDraw.Draw(self.__arrowImgSingle)
        aw = w//4
        ay = h//2
        draw.line((0, ay, x2, ay), fill = 0, width=lw)
        draw.line((x2 - aw, ay - 0.7*aw, x2,ay,  x2 - aw, ay + 0.7*aw), fill = 0, width=lw)

        self.__arrowImgDouble = Image.new('1', size, 255)
        draw = ImageDraw.Draw(self.__arrowImgDouble)
        aw = w//4
        ay = h//2 - 0.8*aw
        draw.line((0, ay, x2, ay), fill = 0, width=lw)
        draw.line((x2 - aw, ay - 0.7*aw, x2,ay,  x2 - aw, ay + 0.7*aw), fill = 0, width=lw)
        ay = h//2 + 0.8*aw
        draw.line((0, ay, x2, ay), fill = 0, width=lw)
        draw.line((x2 - aw, ay - 0.7*aw, x2,ay,  x2 - aw, ay + 0.7*aw), fill = 0, width=lw)

    def __goodRotate(self, img, degrees):
        w = img.size[0]
        h = img.size[1]
        bigImg = Image.new('1', (w*3,h*3), 255)
        bigImg.paste(img, (w,h))
        bitRotatedImg = bigImg.rotate(degrees)
        return bitRotatedImg.crop((w,h, w+w, h+h))

    def __get_trend_image(self, trend):

        if(trend == Trend.NONE):
            return None #"**"
        if(trend == Trend.DoubleUp):
            return self.__goodRotate(self.__arrowImgDouble, 90)
        if(trend == Trend.SingleUp):
            return self.__goodRotate(self.__arrowImgSingle, 90)
        if(trend == Trend.FortyFiveUp):
            return self.__goodRotate(self.__arrowImgSingle, 45)
        if(trend == Trend.Flat):
            return self.__goodRotate(self.__arrowImgSingle, 0)
        if(trend == Trend.FortyFiveDown):
            return self.__goodRotate(self.__arrowImgSingle, -45)
        if(trend == Trend.SingleDown):
            return self.__goodRotate(self.__arrowImgSingle, -90)
        if(trend == Trend.DoubleDown):
            return self.__goodRotate(self.__arrowImgDouble, -90)
        if(trend == Trend.NotComputable):
            return None #"NC"
        if(trend == Trend.RateOutOfRange):
            return None #"HI"
        return self.__arrowImgDouble.rotate(0) #"??"
        #self.__lcd.write_string('\x02\x02 \x02 \x03 -\x7e \x05 \x06 \x06\x06')

