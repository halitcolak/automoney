import argparse

from config import Config
from websockets.message import start_websocket


def main():
    parser = argparse.ArgumentParser(description="Uygulama açıklaması.")
    parser.add_argument("--symbol", type=str, help="İşlem yapmak istediğiniz sembol.")
    parser.add_argument("--interval", type=str, help="İşlem yapmak istediğiniz zaman dilimini seçiniz.")
    parser.add_argument("--position", type=str, help="Açık pozisyonunuzu belirtiniz.")
  
    args = parser.parse_args()
    
    Config.symbol = args.symbol
    Config.position = True if args.position == 'True' else False
    Config.interval = args.interval
    
    start_websocket()

if __name__ == "__main__":
    main()
