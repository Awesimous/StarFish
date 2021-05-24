def weather():
    degree = int(input("Temperature today? "))
    if degree > 15:
        print("Ideal to go for a bikeride")
    else:
        print("not ideal weather but you can always go for a quick ride")
    
if __name__ == '__main__':
    weather()
