import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons

# Luodaan kuvaaja ja asetetaan tilaa radiopainikkeille
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.3)
t = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
s = [i**2 for i in t]
line, = ax.plot(t, s, color='red')

# Radiopainikkeiden asetukset
axcolor = 'lightgoldenrodyellow'
rax = plt.axes([0.05, 0.4, 0.15, 0.25], facecolor=axcolor)

# 'labels' sisältää radiopainikkeiden vieressä näkyvät tekstit
radio = RadioButtons(rax, labels=('red', 'blue', 'green'), active=0)

# Funktio, joka käsittelee radiopainikkeiden klikkaukset
def colorfunc(label):
    line.set_color(label)
    plt.draw()

# Liitetään funktio radiopainikkeisiin
radio.on_clicked(colorfunc)

plt.show()