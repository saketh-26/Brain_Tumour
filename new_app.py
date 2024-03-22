import streamlit as st
import cv2
import numpy as np
import sqlite3
import bcrypt
from ultralytics import YOLO
import pandas as pd


# Initialize SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
''')
conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def signup(username, password):
    # Check if user already exists
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone():
        return False
    else:
        # Hash the password and store the user
        hashed_password = hash_password(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return True

def login(username, password):
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if user and verify_password(password, user[1]):
        return True
    else:
        return False



# Function to setup the background image
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url({image_url});
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image URL
background_image_url = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAoHCBUVFRgVFRYYGBgYGBgYGBoYGBgYGBkaGhgZGRgYGBgcIS4lHB4rHxgYJjgmKy80NTU1GiQ7QDs0Py40NTEBDAwMEA8QHhISHjQrISs0NDQ0NDQ0NDQ0NjQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NP/AABEIAIsBagMBIgACEQEDEQH/xAAbAAACAwEBAQAAAAAAAAAAAAADBAIFBgEAB//EADsQAAIBAwMCBAMHAwQBBAMAAAECEQADIQQSMUFRBSJhcYGRoQYTMrHB0fAUQuEjUmLxooKSssIVM3L/xAAZAQADAQEBAAAAAAAAAAAAAAABAgMABAX/xAAkEQACAwADAAICAwEBAAAAAAAAAQIRIQMSMUFRImEycYFCE//aAAwDAQACEQMRAD8A+YipKK4BRAK6zlPAVMCvAVICiY8q0QLXUWiBaIDgWuhantqQWsKQC10LRAtFs2SxAHWsZugSpUglXdnQqoyJPrTH9Op5UfKj1ZF8yM5srxFWGt0uxscHI/ak2WgUUrVggtSC1MLRrNrrRM2LhD2rhtmrHZXClAXsVxFcApm/bigRRGs5FeK1OK9FYxACuxU4roWsYHUlSiFKkqVgEQtSCUQLRrSdawG6F2WKcS2SAeJoSLJJp3TnpRWCSYIW45ov3dHcCKij4xTE22V15Mmglas3szQGsUCqkJ7aiy0yyUMrRDYDbXttG214JWYbAoIM1YbQwkUBLJNS+7ZeKmxJaQuJSGpGRT1y638FIuJ5rDRT+Ra4lKOlWBpdxQZRMr3FRpi4tAilHTJKKIBUVoi0wToFTAriijpaJogbJW0xRQlFS3Rlt1hWxYW6kEp+3pZ/YU6nhRPJj61qZOXJGPpTpbJ4FWnh2lIJJFOLotg79zTGmWDHeilpKfJawiEruymnt9a8lvqapRz9ip8VTyr7n9KpytaTVqGPGBxVZqdJA3Lx1Halcfk6OOVJIrwlNWlxUNtFsvGDSWVl4T21ErRoqLMBWEFdQnFB+6ps5rxWsNdCRt1zbThWgutYKYErUgtSiuqKwxwLU1WpBakq1gHFSmbS4oYWjWhFawS8BFCD6UW28UxtBFQFimItkLrkiKLYQ10IBxRUf0o2amTKUMpTETXilYCwRvWqUe3Vs6YpN0rFIsSKVNEorJXba5oWM/Bmzage9RdKZtiVFccUTmvSp1NrrVe4q51C4NVF2lZfjdoXcUB1o7ml3alZVC10UCKO7zQaUc8ooiiuIKcs6XuaYLdErFjqaetWZoo08AHpTNhKJNyOW9OKKumzNMIlHtp+VEm5MJodPA3dTx7U4tvNd0y+UUZUqi8OSbtkTbBx0NIbIq1A69qReBliB/O1LIEGwb3mA56gcD3/AEof3jNyaBqNRLDsP5NMIMijHSjhSOOmKiySjf8A8n8qK9C1T7V29W+gppfxMrboqCtdCUUJUttROpsBtrmyjFa9FYFkQteIrwaukisBoGaC1EdqhNYaJACpBa6K6RWCSVakgryUa2tYDZwLRra1NbVECRWFbIqtTArwFTArCsjsroWp1xVrGGNOtSYAVPTLU79qmsHWxO52FBZKZK1P7ugwrCua3XBbqx+5oq6cAT1oGlKivR9tedx3pu7bqt1KRRtoSlJi2quYgVVXTTd6krlBsvCNC7ml7h6Ue5QiKVlBVxQdtGuCgzQGGtN3p+29I2hzT2lt7mC9z/3TKxZUXemEpB6j/qp6cTRAkD4QP0qWktnms7smqoatWhRbluBIrqA0YJWsm0D0V8DDcflTpup3+hqv2QSPWiispMWXHFuyV+/OFwPqarry5NPbaVcSTRuwxil4KOld0F5ySBBA700tmacTQhcjr/gzTRHksFnJPYe1KXbDDJzPX96sXtj4z29+p64r2zcCO/8ABTSWE4vqyq210ipsK4lpmIVVLE4AAkn0A61MqwRo+k0LXAWlVRfxuxhVngYBJb0AJqxs6X+n8122HuE7VRoZU6l3GZMcKe8kVZadv6kb7gJs6dSdo2r947E7RCiFUAdOAOsyVcvoaMbKnT+GW2youXV3AFzts2xJjlpPfkjijvprDXFsaewLrkx94z3Ak9YUPkAT5ienFBe3e1O+4F8iDyqB5EXGFA9wT9c13wbxg2GUqBz5gcgjsOonvQ0bP8LVPBtNaB+9v2FYRuC2y8TmEN1mB5520rd1WjMqLl8QCVIIRSeiwiGBj/b+1P67w+3qVa7bYkgbmTEjtP8AuXnzClPBfBlUvqL4/wBO1kKcb25Ag9Bj+Zpcq2xtuksElDX9qJaJQkAs4a5tE5YXCFKLGcRXja0yK27Ts7oJb/VfYJMAqyFgVMg81PW+I3NRYv3GchUZFRFlU87GSQMHyqcetE8FsEWNRIEf0+Z4BLKRn/3fKm+DesEmg019S1oHTtJAFxmNtyIJUOxJDZHXqMVF/s/qEUsyAxkhWVmA7lQZipfZ/SvcW5aZTtZCQTG1WP4XI7g59gaLode1pAi3muOICqglF/4q58zewAo6vBGk1bKxDRFq5OlS87qyC3cTLupUWpH4t8kAZMSOTnNVN6yyMVcQR8j6juKKlZGUWiDp1rkUSaktEFglWiKtdZanaGaKCOaWzRr9vFT0z0XUZFBvR1H8SpKZoqJUxazRhbig2KkC2UdrZqVu3V1pNGGFByob/wA3IzdyyarNZbxX0J/CQRWW8c0W2aykmZ8Ljpjb6UhdFW+oSkL1s0wyZWOKCTTdxKVurS0OmLXBS8GmCprv9OaAUMLpWB4q/wDBtCYLlT2H6motfWa1GkvIqKPQU7wX+RXf0rE5pvT6M9qcXUJTC6pKWxuqEvuYqVE1GoB4paSa3Yk46DKZmibamFoqpS9guAm88RFDa31qyNuaYt6MEU6Zuj+Cu0yiRV3qdmwbPxDPxqsvaYqcVG1qSMeoz1x69KJkvgDcblcZK8wJmSMnjnn9KAX2jd0qWpYKzCQQc4UFhtBggxkdeaVdyQRgCI/CMzjtjr6gj0rdgOIvaBY8SSYAHJJ9K0CK+ntbkje7MjuudgEeRW6EmZI7Y70H7J2EN+X4RHecQpAHmPsCfjFW6+N6a0DbVSUYiS5B3SZ3HEevQcUrvxIZJet0KeFH7mw994cO21UYAqWAku0iTEwAO5qOk+0aLuR7YCMDm2ipBIidvU4HX51dNYsam2ioVQAsVUQJJMSDPWP5FVus0VjSErcG93UrAaNtsxJyPxEiAPrSun76Mk1VPDPjfYdLtlgyMxVTmDxuR15HI98Qas/Gk0Vp827m9lVmtqwVBuUHDQSRJIxGRS+s8FKhbtly9ssGE8qZ/uUdR9elW32h8NtvcF6/cCBkWbYln+CjmTuzgfKt8ozTSZnfCdVfVi9ohQmSzHaiKTADMxiCcBck+tOanxfUatHViotogZ1QbdwDAAAcgEkfD5UJNUt29ZsKmyyLqeTEsSY3OeC0EiOBMZmaY8YuW9DaaySpvXB/qH/am6VX3JAk9KL980yTrHh77LaT71LtkgFXWfQOolTPfj61pl09nT2Dbu3ERnjfmWIyQoHOJ5Pek/sHpj92zx+IKw/9pCr8wTH/ACqs13g4dybuqQOZO0BngzJ3MIVWk0r/AClQ9dYp0Ed2uIU0y/do2GuOdpfPA7Dnif2c8H8O02ncB3DujAEqCVQ4HmY4me3xrOpaS24dCXKhmSV5YDySM8ET8K6ujuNaF5W3QxDKDnEzjqJn5e8PKNZYkZW7rS21imxfurcBNq+SdyxEF96uDwYA496jc0bOgQHfAJsvwTBG62wPBgggTnGY554T4w+0I4DoxIZGzg87ew5xwYNWQ06or21wWZLthmO0OCAAgJ/ughY9qTUHqmZZFnFH+7p/x61tZLvH3gYODgi5bO1598H3k0glyasqas5ZRalQRbc1NLWas/CrSMTvMAAmvNpvNjj9KXtpRRwHbSKI5FevDsIzgZMdhnmuJMRPMTgVrD+hnTWARNRvWgK9bcjFdczU36VVdaRCwuavtEKpLYg1baW+KEikC33YrN+P25Bq4uaoAVR+JX9+KWPoZ+GPu2JMVI+Gys1aXbEZpS7q9oirWQUaWma1+m2zVNfWr7X3ZmqHUtRYEtF0eDTP9SKURJNH/ozQHwZu3IrS6OXRWHUCsTcvFq1n2e1X+ko7Ej64/OmbBVDrkipWmJqF4FjRNOkUkmZKx+wKOLY6UOzTKf4pGwqJz7r1qSqP+ya8z1O2JpHJ3RaME1ZxhFFTVgCu6y15ZrM6rVMpqkX9iOP0XN/UEnFet295kDPbvVHZ1ZxVxodbtIYdKa/oHVINqdNsG7IMHjBAIgj2MwfQnvVY9pwITKkzG3d6Ru5+AI6VoNXrDclu4nGPy9arVQGQQTPfJHeDiMflVIRtWyM5JYM+GadlsO6qhuBthVxKFCuQVkcjcJmnL/h1oyRp9zBUZx97sRSy7iVkEwDjPJI+EvC2W0Su4FXA3cgKQZGT1B68VcPpEbcGkb02tHUALtaeP7Qf+6WTpmguyKnw7SWHU7d1lv8Aax3KPiR9K54l9n71/YWdGCKUDhuRM+aT04qzTw7gBgeMjy59O3fHemxoTEA4iBwBP6e2aSUtxlY8eahJE/ptMVtsruCqsR54J7/I9OvFUyeEvdcu7hl5dwZbiT5eQSAAPbtVzf8ADGUECdrc89/Q8TwPjJJNE8P0xAdY5QiffMDp0+uJrRdJtGlG2k1hSeA+HL9698KB92CUU5hiCoJ7kfnWWveDnU6srduhUB3OzHzMT/aoiC5iO0AdhWy8GuGyXlSRtiB3JAzHIGc0t4V4Qz3mcqQDkdeTMA9QIGR2pnVtv/BVaSSX9ln4wRp7C2rWN0y3WOpz14/6FZnQeHPdY7RgwfzM/M/Stp4rpkZlZ3AAgBeregHbiqPW/aVLY2WIEYkdfc8zgUONtLFo3Ik5W3gxqfAyls7Vk7SJxiRBMnAOT/DgP2d0otoWIlWYKVOVIwsjpPJkdG6iKqdNcvat9u5tuN8Ewoz+1a1dOlsAv5URYQd+/r0GaE7SpvRuNJvslhnfE/Bfu38oJB7TnIBOOOOKN4na1LZtSE2BFH9pVRAJU4DE59KsLv2ot+Yi2WUHLcgE8ST39J+tc8I133t17gLlQCPuywOFXd5VwIMr0/wE3VtGcY3SfoPxXw1r2nJYf6qs91FGSwhQwHcnB+VZfRKpILTtkSRzHpPWtmmsa6VcDYyPDgeaFYQY+MA1nvGtMF1DogAEqQAQACyqx+pNNB/8snzwWSR3TMBAzJOZ7fh6fGrDTuCBMdoEz33Z71X20EhsEYxInGAD6mJ+PzdRZZoWBJP9xgT3ngTRZOLHFtzx1B7REZ54pf7nmOe2Z68U3ptVsyAM4zOa4xMzMH0xz7Ul0UrsKpbj41IrUmbtUGeBWoZL4R411XIoFu4Hz0orVmhqZy/qoGTQUcEzzSXij7RVboNbO9D/AG5Hsefr+dFRVYJJtO2WviN4AYrL6y9FO63UmqPUvIJp0qEbcnYrqr9VV15NN3xSDitJUNEj95FS/wDyVLXzAmkZpGyiimWZq++zN3yuvZgfmP8AFZ3dT/gmqCXCv+4R8RkfrTWI/DahxRLZqqS9NWGmekkzRiyztUdDSqvAmmdMZAPpQSKE7i+YDuMfrTFoRUmQMIPuPQ+lL2XzU5Y7Lx1UWbLuWKx32h0ZSW5E/KtgtyFmcVm/FtUpnqDIis5G6GbtXCKs9NciI+FVgRSo2klsiCMcwAIyTx2p7RXH2gEiFDEyw24nco6A4+OPi8ZUyco2jQ6TkrKypgAGSwIM7ehAj/yp9bAaCuO4GZ+P8+FZzT3CYAnG3G2CcDt6z6n6Vb6Z2GYO0ztkcjIkDgcH5VZcn0QlxJ+jRtz5MjOARmek5jNHW5dSIZlXAyJXME+UyDzXX1UQDC7QFBxBI7+pqd681xpbpluBgdZ7+lFvsKoKABPGnkSqEdIUq0SeJMTHpVnp/EE/vQpHLLDLBH/GDx6E1VBd5EySAAPYYAJ5IA9vemLjstsoB5TmQMEjEz6SKWUR1PfTSabVoylkcOBgiZPswOQTUnvIi732oDMgnJB9PWsh4HbKNdvkH/TTC/7mYwAe4ETHtStmy+rc77wVmnasMZBPB6dPqKk4b+iinizTQ6rx/TWySEknJ/snEzGScfzNUmu+2TnFpVWQRIG49eC3T0phPs3ZBl7m4jEDcfb8I4+NWWn8O0422im9id3lTYFHUuWY9PjwPSji/YHb+aMtpfD7+pMhYHXy7evU9TEnqfzp4fZfZ+NkXjLuon0Knp7ZwatfE/FXH+lp0wDtVVBBgHJhcxHtFVj+A6h4d3CEGSCQpJPWZ7wP+op+z/oRQj8K2WdjxXTaRApfe3XYpPA4E9B6k+pqm8bvjWOCj3QpiAyqqADlQeZz6njpVnovslbgG4fN2DDAiZxM+/xr17xFEfZpU3vhWuQSByAqDqcc+8eiZdoptU8RHWaG3p9PaRke4yjcyIY8xg73MT7e5qf2RtbizxAkgRMRtOJ6jPJ5x3odvwG+zFn/ABNlmZ1Ek+2QBJAxj3q9+8TTqEXzMQSABwsFix9DHyHoaDeUgqO28AeH6DzlshdxYDnJ/ny9qo/Gl3am63QEDjsoUn1GD8a0nh18kNdeQqgnMCNv4vyH1+OZNxmLBtmXZxAnLGT5xmP800LtsnzV1SAW8+3T96sUt8nIkAn4wf1r1jTAzMDHSc5Hf9Kc2QIExABnv8BxinbIpIXtDP0FSuvGBRVAFQvIRkikbVnRCDrSFtJqGot4NSW9FL6q8QpIBI69TR7IaMRfRDAHqR8jTzuFFVHhWpyQwIgnaT1ntQvG9Q0eU0nZDuLQDxe8G4NVHh0l2bptg/EiPyNIXNaTirHSttSepz+1W4l2ZzczpHNc4FVNxpo2puSc96XuGqUiQtdFJOtWEUpqXCgmhJDRZV6xsx86UijOZzQoqLLpjbnFLEkGeCMijBxQ3YVmBGj8K1wcdmHI/UelaDTPivnVu6UYMpgitT4P4wr+U+V+3f1FKM0apbmKe0D4qltXZqx0VyKKMXKGqywz/eXARhX2z2BVWU/+UfCnrd8UF3AuEf70DfFTtb6FflWnFOJoSakKeM+JbRtB4x8qyV3WFmqy8c0V1nJRSVPqPrSF7wdlt72eG3AbAsyCCd26ehERH5VyVtnc3+NIY0CiIA80nJOIMYA6HB5kGemZeGlOW74PaOf2iq7wwwRLD5N9cVr9Zo9iId4YMJABPlnpB4nFVi0c8kyne7sPkjMSCsqpYSQFMz6M3I6A1c+DMWABKjaGfJInMER1JIXHWqUp5ieoCjbH4uQRP/pFWWluwEAyMz/xMnk9Y78UYyVitYXjbQBEcZmc5OY4/THFcDA4MTiInjsBEdvlSzX1I54ww7GTiotqFA7zx+9VU0mTlxtqiyRFEEHzHkQBHaP5ivX0Ugx2656yY9KU0+oUgNJ3EkERx6z605ZQv+EEmDiJ6Hj9qq69OXpK6I6O1ut3U6nY3uFJBj50p4ZutuW2yxBA5yT1/wA1IaprT7lk48w4nGQQOk8H2PpT1rxHTMJkI4yVbAk4MNEUrdX+ysY+bqPabw68ed3PU4n1+vzx6Wdu4FMuQ7RthMwsHM8TB496WfxJIE3bZgR5XTjMnnmM1BdZZyWuoBydrbjHaFnr69O5qbbfpVJLwMdIwJdCCHG2RggTwOo/7qvfwc8kyfX6kj+cCi677UW0HkRnC4z5F3ZwTBM84jvV3p9SrIrhQQ6qy4gwQIEnrJrdpIPWLKB9I6p91akBmJuN/ex5gxwI/T2qWg0ly2PIoBBmdonIM5PE9+SMelWtzxKyGKCJA6FY9uY6/rRF1lowWLxzlTt+g5z8aVtsZRS+SpddQxksVmIwIA5Lt69h6Uxo/BfNvdmLZifNt3cx3bjPTpirA6qzPUnoCp/X9aKurQnZJn4jHcnECtb+A0vkoftF4iip/Tpk/wB4B/CoztJ70lplWEEBcdDumYyTOD6fSqa5Z2XCP+R29cbiN2D6GPn72+ikLJU4aM8ZyJHJ4Oav1UY0jmbcnpepo4QNIj3oTQJ9ewodq+SvpJwOPTn41IuQJUx7dO/7VJtorHjXpxBmI9cn5US85YBTwOP80O20fH6elNx6Uqoo20IPpOtCvaXYJPyq4VxGSBA7il9SEYZ83vxRMmzEau+S5KhscnkCO/aqm94huaGOM/lWu8Vu7VIQD2gR8q+ea9GViYj40jS7DSb6nEsyw9WAPuzR+tX160AIrOabU+e2n/LefZQSPr+VWmp1Vd3FKKVnn8sZNgtRaEgUpeUCoDVlmJ+VLXb0mtKcTRhImzRVLrL+5scD6+te1+u5RT7n9KrvvajLkTwvHja0ZNRigC5XvvaTsh+rIh68XqFcqdleqJFq4HIMgwRwRUa9Qs1Gp8E8cmFcw3Q9G/Y1qrGqGM/CvlorWfZvUMyeZiYMZp4u8Ekq02dvVUzcbcFYcqZ+HDD5fkKzoczzVx4cZ+RqjVoknTLq3pt4j+RVd4noXXcCsYwPYj9Jq88P4X3/AEqXizksZM+U/wDxNcbR3x8MKlqDMTmAO57e3E/DvTiaslirEleAck4GGx/DJqV9oJwuHWDtWR5d2DE8kn5dhQNLdaQZOJ/I0ANDN2yUlGDK48rggSDLNC5mI2gnue3JtM2OwAgTzzM455Ik9O0Cg22ggiB5egA/tI6UZDAbj+3oO7VjJWOqVDhtu5cblYxux5hIyBNCuXusCfn9DNQfikrhpWx0kWek1XmiYntA/KrjTasrkEz61jbTkMueorS118D7RpnJzrrK0Tv6nzbiSDmGXDAwY+E1UXUHp+1O3qXAyKtVELsFYtCcgkckDEgc+3apXE646AzzxxB6YIntHtR7fB9h+dH09sGZH8kfvQaCmVt20ZM5Ag9SAeY7E4I7VtPstrg9nY0KyGGUr0MxC/2j6CKz9i0DukT/AJIpr7L/AP7x6qwPqO1JJWh4YzUXdYm0ugVtoBIgFhPBjmKgniKsAC2w9JEr8+Kr7JksMf3DgcfwVB7hi1wdxXcCAQeeQcUhVlu2nuN+G58QAoHyAk1S+MeJJbUpZIdz+JywgHj/ANRz7fWLjx0/d6a7s8sIYjp0r53vJYSeE/8AoBT8ce2snyPriG0YuSWYAmWmcH0heCf0qy0trp3j9eKqdP0q78OuEAieYq0sVkYq3RZ2rZiOePWf5NG2Z3AAQcc4I96Ap/nwqw0/6Cuezp8F1tNM898kfrRFtY/ejNXkoA7MrrqEc56fz6UlqdQQKvvEEGxcVmdfwanKTOiMU0UPiWqYzWQ19ws3NaTXVl9X1/nWki22HkSSA+GjdcL9lx6dB+tH197+0cn8q74WMN70ufxn3rsisOCTtnlWBVZ4hqolVPm6nt/mrbXnbaJGDFZmhJUNF3oDYa6ENMVE1Oilgvu6993UzXqNGtn/2Q=='  # Replace with your actual image URL
set_background(background_image_url)

# Initialize the database connection
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create the users table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS users(
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')
conn.commit()

# ... (Other function definitions remain unchanged)

def add_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_user(username, password):
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0])
    return False

def show_signup():
    st.write("### Sign Up to Brain Tumor Detection using YOLO")
    new_username = st.text_input("Username", key="new_username")
    new_password = st.text_input("Password", type="password", key="new_password")
    if st.button("Sign Up"):
        if new_username and new_password:
            if add_user(new_username, new_password):
                st.success("Account created successfully! Please log in.")
                st.session_state['current_page'] = 'login'
                st.rerun()
            else:
                st.error("Username already exists. Please try a different one.")
        else:
            st.error("Please enter a username and password.")

def show_login():
    st.write("### Log In")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    if st.button("Log In"):
        if check_user(username, password):
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Wrong credentials or user does not exist.")

def show_yolo_model():
    # Load the pre-trained YOLO model
    model = YOLO('best.pt')

    # Read the COCO class list from a file
    with open("coco.txt", "r") as my_file:
        class_list = my_file.read().split("\n")

    # Streamlit interface
    # st.title('Brain Tumor Detection using YOLOv8')
    # st.write('Upload an image and the model will detect brain tumors.')

    # Upload image through Streamlit
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file is not None:
        # Read the image
        frame = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)

        # Resize the frame to a fixed size (if necessary)
        frame = cv2.resize(frame, (1020, 500))

        # Perform object detection on the frame
        results = model.predict(frame)
        detections = results[0].boxes.data
        px = pd.DataFrame(detections).astype("float")
        # Display the detected objects
        st.image(frame, channels="BGR",
                 caption="Uploaded Image with Object Detection",
                 use_column_width=True)

        # Display the detected objects and their class labels
        tumour_count = 0
        for index, row in px.iterrows():
            x1, y1, x2, y2, _, d = map(int, row)
            c = class_list[d]
            
            # Draw bounding boxes and class labels on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0, 255), 2)
            cv2.putText(frame, str(c), (x1, y1),
                    cv2.FONT_HERSHEY_COMPLEX, 1.25, (0,255,0), 1)

        # Check if the detected object is a tumour
            if c.lower() == "tumour":
                tumour_count += 1
        # Display the frame with objects detected
        st.image(frame, channels="BGR", caption="Detected Objects", use_column_width=True)
        # Use HTML and CSS to style the text
        st.markdown(f"""
        <style>
            .tumour_count {{
                font-size: 24px;
                color: red;
            }}
        </style>
        <div class="tumour_count">Number of Tumour Detections: {tumour_count}</div>
        """,unsafe_allow_html=True)


if __name__=='__main__':
    st.title('Brain Tumor Detection using YOLO')


    auth_status = st.session_state.get('auth_status', None)
    if auth_status == "logged_in":
        st.success(f"Welcome {st.session_state.username}!")
        st.header('Upload an image and the model will detect brain tumors.')
        show_yolo_model()
        
    elif auth_status == "login_failed":
        st.error("Login failed. Please check your username and password.")
        auth_status = None
    elif auth_status == "signup_failed":
        st.error("Signup failed. Username already exists.")
        auth_status = None
    # Login/Signup form
    if auth_status is None or auth_status == "logged_out":
        form_type = st.radio("Choose form type:", ["Login", "Signup"])

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if form_type == "Login":
            if st.button("Login"):
                if login(username, password):
                    st.session_state.auth_status = "logged_in"
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.session_state.auth_status = "login_failed"
                    st.rerun()
        else:  # Signup
            if st.button("Signup"):
                if signup(username, password):
                    st.session_state.auth_status = "logged_in"
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.session_state.auth_status = "signup_failed"
                    st.rerun()

    # Logout button
    if auth_status == "logged_in":
        if st.button("Logout"):
            st.session_state.auth_status = "logged_out"
            del st.session_state.username
            st.rerun()







# # Main app flow
# if 'current_page' not in st.session_state:
#     st.session_state['current_page'] = 'signup'

# if 'logged_in' not in st.session_state:
#     st.session_state['logged_in'] = False

# if st.session_state.get('current_page') == 'signup' and not st.session_state.get('logged_in', False):
#     show_signup()
    

# elif st.session_state.get('current_page') == 'login' and not st.session_state.get('logged_in', False):
#     show_login()
    

# elif st.session_state.get('logged_in', False):
#     show_yolo_model()
#     if st.button('Logout'):
#         st.session_state['logged_in'] = False
#         st.rerun()
