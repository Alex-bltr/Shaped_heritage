import pygame
import random
from time import perf_counter
import time
import hid
import threading
import queue

reaction_start = 0
final_time= 0 
button_locked = False
button_locked_2 = False

def worker(q):
    global final_time, reaction_start, button_locked, button_blocked_2
    
    VENDOR_ID  = 0xeb7  # Deine 5227 dezimal = 0x146B
    PRODUCT_ID = 0x20  # 1541 dezimal
    REPORT_LEN = 64

    dev = hid.device()
    dev.open(VENDOR_ID, PRODUCT_ID)
    dev.set_nonblocking(True)

    last_button_state = 0

    try:
        while True:
            data = dev.read(REPORT_LEN)

            if data:
                button_state = data[2]  # Achtung: Index anpassen je nach Gerät

                if not button_locked and not button_locked_2:
                    if button_state == 1 and last_button_state == 0:
                        q.put(1)
                    elif button_state == 0 and last_button_state == 1:
                        final_time = perf_counter()- reaction_start
                        q.put(2)

                last_button_state = button_state
            else:
                # Kein neuer Report – wir tun nichts oder könnten idle-Zeit ausgeben
                pass

            #time.sleep(0.01)  # wichtig, um CPU zu schonen
    except KeyboardInterrupt:
        dev.close()
        print("Beendet.")


def main():
    global final_time, reaction_start, button_locked, button_locked_2
    #print(final_time)
    q = queue.Queue()
    threading.Thread(target=worker, args=(q,), daemon=True).start()
    GAP = 5
    AMPEL_WIDTH = 110
    COUNT = 5
    total_width = COUNT * AMPEL_WIDTH + (COUNT - 1) * GAP
    start_x = 1920-total_width-275

    pygame.init()
    display = pygame.display.set_mode((1920, 1200))
    clock = pygame.time.Clock()
    run = True


    font = pygame.font.SysFont("Arial", 70)
    reaction_time = 0.000
    

    clicked = False
    ampel_step = 0
    ampel_last_change = 0
    wait_time = 0
    wait_start = 0
    ready_for_click = False
    early_click = False

    font_small = pygame.font.SysFont("Arial", 30)
    font_input = pygame.font.SysFont("Arial", 35)
    font_1 = pygame.font.SysFont("Arial", 40)
    input_box = pygame.Rect(280, 350, 415, 50)  
    inp_active = False
    text_input = ""
    rang_rect = pygame.Rect(280, 420 , 415, 420)
    Rang = {}
    box_liste = []
    box_count = 0 
    #cursor
    #start_time = 0 
    #visible = True
    current_pos = 0
    haeder_font = pygame.font.SysFont("Arial",70)
    '''Das Problem ist ja eigentlich rehct leicht es geht darum das ich zwar dieses Ranking erstelle aber ja die positionen der boxen eben austausche 
    und die texte sind ja eben an ihre box gekoppelt weil durhc die box kooridnaten der rest berechnet wird
    heißt es kann passieren das sie dann nicht mehr in den top 5 sind okay kein problem heist am besten hätte ich ja eine liste und prüfe da durch weil 
    einer seits habe ich ja die boxen deren ranking sich ja ändert '''


    big_box = [rang_rect.y + 80 + (55 * i) for i in range(5)]
    # hier kommen die aktuellen Top 5 rein wie mache ich das aber das ist die nächste frage
    class Leaderboard:
        def __init__(self, dic):
            self.dic = dic
            self.box_counter = 0 

        def update_rang(self):
            scores = []

            
            for i, name in enumerate(Rang):
                scores.append([i, min(self.dic[name])])

            scores.sort(key=lambda x: x[1]) 

            for platz, (original_index, _) in enumerate(scores):
                box_liste[original_index].y = rang_rect.y + 80 + (55 * platz)
        
        
        def draw_board(self):
            mytext = special_font.render("Bestenliste (Top 5)", True, "white")
            display.blit(mytext,(rang_rect.x+15,rang_rect.y+10+5)) 
            self.update_rang()
            #wenn ich eh schon darüber weg iterriere dann kann ich ja gleich über nur die notwendigen in der liste iterrieren heist
            #heißt eigentlich pberall dort wo ich een das ranking ändere muss ich dann hak t eben das in top5 die liste hinzufpgen damit 
            #ich dann prüfen kann ob das zu biltten objekt in den top 5 ist #
            '''IDEEE: ES GIBT NUR 5 spezifischen ranking POSITIONEN HEIST DIE POSITIONEN KLATSCHE ICH IN IENE LISTE UND SAFE DANN WENN DIE 
            POSITION DES ZU BLITTEN OBJEKTS DANN BEN ENTHALTEN IST IN DER lISTE DANN KANN ICH DAS MACHEN'''

            for i,key_val in enumerate(self.dic):
                    if box_liste[i].y in big_box:                
                        pygame.draw.rect(display, "#ababab", box_liste[i], border_radius=15)
                        name = regular_font.render(str(key_val), True, "white")
                        display.blit(name, (box_liste[i].x+10,box_liste[i].y+5))
                        wert_str = f"{min(self.dic[key_val]):.3f}"
                        record = regular_font.render(wert_str, True, "white")
                        display.blit(record, (box_liste[i].x +box_liste[i].width -100,box_liste[i].y+5))
                        self.box_counter += 1
                    else:
                        pass
                    if box_liste[i].y == big_box[0]:
                        display.blit(first_p, (box_liste[i].x +box_liste[i].width -150, box_liste[i].y+10))
                    elif box_liste[i].y == big_box[1]:
                        display.blit(second_p, (box_liste[i].x +box_liste[i].width -150, box_liste[i].y+10))
                    elif box_liste[i].y == big_box[2]:
                        display.blit(third_p, (box_liste[i].x +box_liste[i].width -150, box_liste[i].y+10))

    class Ampel:
        def __init__(self, x):
            self.width = 100
            self.height = 336
            self.x = x
            self.y = 425
            self.lampenfarben = ["#1F1F1F"] * 4

        def set_lampe(self, index, farbe):
            if 0 <= index < 4:
                self.lampenfarben[index] = farbe

        def reset(self):
            self.lampenfarben = ["#1F1F1F"] * 4

        def draw_ampel(self):
            pygame.draw.rect(display, "black", (self.x, self.y, self.width, self.height), border_radius=11)
            for i in range(4):
                pygame.draw.circle(
                    display,
                    self.lampenfarben[i],
                    (self.x + self.width // 2, self.y + 50 + i * 80),
                    36.5
                )
    ampeln = [Ampel(x=start_x + i * (AMPEL_WIDTH + GAP)) for i in range(COUNT)]
    start_time = 0
    visible = False
    butpresse = False
    start_time2 = 0 
    gamecount = 0 
    current_player = ""
    violation = False
    font_3 = pygame.font.SysFont("Arial", 40)
    image = pygame.image.load("C:\\Users\\alexg\\Documents\\shapedheritage[1].png")
    scaledimg = pygame.transform.scale(image,(450,225))
    image2 = pygame.image.load("C:\\Users\\alexg\\Pictures\\trophy.png")
    image3 = pygame.image.load("C:\\Users\\alexg\\Documents\\platz2.png")
    image4 = pygame.image.load("C:\\Users\\alexg\\Documents\\platz3.png")
    first_p = pygame.transform.scale(image2,(30,30))
    second_p = pygame.transform.scale(image3,(30,30))
    third_p = pygame.transform.scale(image4,(30,30))
    gamers = 0 
    alert = False
    lastest_player = ""

    big_font = pygame.font.Font("C:\\Users\\alexg\\Documents\\CanvaSans-Bold12338993995495434039.af71a.af71aaddb4396e5f746d513b7b12c6be.ttf", 110)
    
    title_font = pygame.font.Font("C:\\Users\\alexg\\Documents\\CanvaSans-Bold12338993995495434039.af71a.af71aaddb4396e5f746d513b7b12c6be.ttf", 85)
    
    
    special_font = pygame.font.Font("C:\\Users\\alexg\\Documents\\CanvaSans-Bold12338993995495434039.af71a.af71aaddb4396e5f746d513b7b12c6be.ttf", 40)
    
    buba_font = pygame.font.Font("C:\\Users\\alexg\\Documents\\CanvaSans-Bold12338993995495434039.af71a.af71aaddb4396e5f746d513b7b12c6be.ttf", 45)
    
    regular_font = pygame.font.Font("C:\\Users\\alexg\\Documents\\CanvaSans-Regular9755562880743818424.2de.2de498afbe8ce167560d5df6489c2042.ttf", 30)
    
    smaller_font = pygame.font.Font("C:\\Users\\alexg\\Documents\\CanvaSans-Regular9755562880743818424.2de.2de498afbe8ce167560d5df6489c2042.ttf", 25)
    
    flag = pygame.image.load("C:\\Users\\alexg\\Documents\\raceflag.png")
    scaled_flag = pygame.transform.scale(flag, (800,400))
    top_flag = pygame.transform.rotate(scaled_flag, 33)
    bottom_flag = pygame.transform.rotate(scaled_flag, 185)
    logo_s = pygame.image.load("C:\\Users\\alexg\\Documents\\Logo_bild.jpg")
    logo = pygame.transform.scale(logo_s,(350,140))

    now_i = 0 
    #schau mal wenn ich das ganze latest player = current player nach enter mache dann spielen 
    
    def game_init():
       
        
        line1 = buba_font.render("Drücke den", True, "white")
        line2 = buba_font.render("Knopf, um die", True, "white")
        line3 = buba_font.render("Ampel zu", True, "white")
        line4 = buba_font.render("starten", True, "white")
        display.blit(line1, (1920//2.5,500))
        display.blit(line2, (1920//2.5-20,560))
        display.blit(line3, (1920//2.5+20,620))
        display.blit(line4, (1920//2.5+40,680))
        
        
        #zeit messen und einsortieren 
    #transparent_surface = pygame.Surface()

    while run:
        display.fill("#373737")
        try:
            item = q.get_nowait()
            if item == 1:
    
                if not clicked and not ready_for_click and not early_click and not inp_active:
                    clicked = True
                    ampel_step = 0
                    ampel_last_change = pygame.time.get_ticks()
                    wait_time = 0
                    wait_start = 0
        
            elif item ==2:
    
                if clicked and not ready_for_click and not inp_active:
                    early_click = True
                    button_locked = True
                    clicked = False
                    gamecount +=1 
                    final_time = 0
                    

                if ready_for_click and not inp_active:
                    if gamecount == 0:
                        Rang[current_player] = [0]
                        box = pygame.Rect(rang_rect.x +10, rang_rect.y+80+(55*box_count), rang_rect.width-20,50)
                        box_liste.append(box)
                        box_count += 1
                    if current_player not in Rang:  
                        Rang[current_player] = [0]
                        box = pygame.Rect(rang_rect.x +10, rang_rect.y+80+(55*box_count), rang_rect.width-20,50)
                        box_liste.append(box)
                        box_count += 1
                    


                    Rang[current_player].append(final_time)
                        
                    if 0 in Rang[current_player]:
                        Rang[current_player].remove(0)
                    
                    ready_for_click = False
                    clicked = False
                    gamecount +=1
                    alert = True
                            
        except queue.Empty:
            pass            
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    inp_active = True
                    start_time = pygame.time.get_ticks()
                    visible = True
                else:
                    inp_active = False
                    
            if event.type == pygame.KEYDOWN and inp_active:
                if event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                    
                elif event.key == pygame.K_RETURN:

                    current_player = text_input
                    text_input = ""  # optional: zurücksetzen nach Enter
                    final_time = 0 
                    if current_player not in Rang:
                        gamecount = 0
                    else :pass
                    visible = False
                    inp_active = False
                    butpresse = False
                    alert = True 
                    gamers +=1
                    
                else:
                    #print(len(text_input))
                    if len(text_input) > 12:
                        pass
                    else:
            
                        text_input += event.unicode
                        now2 = pygame.time.get_ticks()
                        if now2 - start_time2 >= 300:
                            start_time2 = now1
                            butpresse = not butpresse
        
        if len(current_player) == 0:
            button_locked_2 = True
        else:
            button_locked_2 = False
              
        now = pygame.time.get_ticks()
        if inp_active:
                now1 = pygame.time.get_ticks()
                if now1 - start_time >= 700:
                    start_time = now1
                    visible = not visible
                
        if clicked and not ready_for_click and not early_click and not inp_active:
            alert = False
            if ampel_step < COUNT and now - ampel_last_change >= 1000:
                ampeln[ampel_step].set_lampe(2, "red")
                ampeln[ampel_step].set_lampe(3, "red")
                ampel_step += 1
                ampel_last_change = now
                

            if ampel_step == COUNT and wait_time == 0:
                wait_time = random.randint(1000, 4000)
                wait_start = now

            if wait_time > 0 and now - wait_start >= wait_time:
                for amp in ampeln:
                    amp.reset()
                reaction_start = perf_counter()
                ready_for_click = True
                clicked = False

        pygame.draw.rect(display,"black", (start_x, 580,total_width-50,40))
        for amp in ampeln:
            amp.draw_ampel()
        

        if not early_click:
            text = f"{final_time:.3f}"
            surface =big_font.render(text, True, "white")
            display.blit(logo,(1920//2-200,860))
            display.blit(bottom_flag, (1000,800))
            display.blit(surface, (start_x+total_width//2-160, 750))
        else:
            #hier muss dann noch hin der bitte rarteb tag 
            text = "Frühstart!"
            surface =big_font.render(text, True, "white")
            display.blit(logo,(1920//2-200,860))
            display.blit(bottom_flag, (1000,800))
            display.blit(surface, (start_x+total_width//2-270, 750))
            warning = buba_font.render("Bitte warten!", True, "white")
            display.blit(warning, (1920//2.6,560))
        
        
        Undertitle = regular_font.render("Meet & Speed | Bilster Berg 2025", True, "white")
        
        display.blit(top_flag, (-200,0))
        
        haeder = title_font.render("Launch Control Challenge", True, "white")
        display.blit(haeder, (1920//4.5,150))
        
        if alert:
            game_init()
                
        pygame.draw.rect(display,"white", input_box, 2, border_radius=10)
        text_sur = smaller_font.render("Neuen Namen hinzufügen:", True, "white")
        display.blit(text_sur, (input_box.x+10, input_box.y - 40))
        # Text zeichnen
        #text in inputbox rectangle
        text_surface = font_input.render(text_input, True, "white")
        display.blit(text_surface, (input_box.x + 10, input_box.y + 8))
        

        if visible or butpresse:
            pygame.draw.line(display, "white",
                            (input_box.x+text_surface.get_width()+10, input_box.y+5),
                            (input_box.x+text_surface.get_width()+10, input_box.y+input_box.height-5), 2)
         
        pygame.draw.rect(display,"#737373", rang_rect, border_radius=15)
        rangliste = Leaderboard(Rang)
        rangliste.draw_board()
        
        #ich muss um die richtige box zu bekommen die differenz zwischnen dem letzten spieler und dem jetztigen Spieler heraus finden 
        now_i = None
        for i, player in enumerate(Rang):
            if player == current_player:
                now_i = i
                break

        if gamecount != 0 and len(box_liste) != 0:
            if now_i is not None:
                current_pos = ((box_liste[now_i].y - rang_rect.y - 80) // 55) + 1
                ranking = regular_font.render(f"Aktueller Rang: {current_pos}", True, "white")
            else:
                ranking = regular_font.render(f"Aktueller Rang:  --", True, "white")
        else:
            ranking = regular_font.render(f"Aktueller Rang:  --", True, "white")
                    

        if len(current_player) != 0:
            spieler = regular_font.render(f"Spieler: {current_player}", True, "white")
        else:
            spieler = regular_font.render(f"Spieler:  --", True, "white")

            
        pygame.draw.rect(display, "#737373", (start_x,290,total_width,input_box.height+60), border_radius=15)
        display.blit(spieler, (start_x+15,300))
        display.blit(ranking, (start_x+15,350))
        display.blit(Undertitle, (1920//2-265, 1015))

        tanzahl = regular_font.render(f"Teilnehmerzahl: {box_count}", True, "white")
        display.blit(tanzahl, (rang_rect.x+10, rang_rect.y+rang_rect.width-45))
        
        #print(Top5)
        pygame.display.flip()
        clock.tick()

        # Nach Anzeige einer Fehlermeldung automatisch zurücksetzen
        if early_click:
            pygame.time.delay(3000)
            
            for ampel in ampeln:
                ampel.reset()
            clicked = False
            ready_for_click = False
            early_click = False
            alert = True
            button_locked=False
    pygame.quit()


if __name__ == "__main__":
    
    try:
        main()
    except KeyboardInterrupt:
        pass
