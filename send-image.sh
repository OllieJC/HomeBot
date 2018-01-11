rm /home/pi/cam.jpg
raspistill -o /home/pi/cam.jpg
curl -F file=@/home/pi/cam.jpg -F icon_emoji=":house:" -F username="homebot" -F channels="#home" -F icon_emoji=":house:" -F token="x"

