# frc-library
A self-service library system with face recognition.  
For 行動學習推動計畫 期中發表會  

# Requirements
- Flask
- numpy
- opencv (with [freetype](https://docs.opencv.org/master/d9/dfa/classcv_1_1freetype_1_1FreeType2.html) support)
- [ageitgey/face_recognition](https://github.com/ageitgey/face_recognition)
- pymysql

## Libraries
- axios
- TocasUI

## Use
```bash
python3 backend.py
```
Now you can connect to `localhost:5000` with browser.  

## Notice
`navigator.mediaDevices.getUserMedia()` works only in secure contexts (localhost or site with https://).  
More info at [MDN](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia#Security).  

## Special Thanks
*in alphabetical order*  
@a91082900 - DB design  
@secminhr - backend development  
@spacezipper - poster & page design  
