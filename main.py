import sys
from coganh import App

def main(argv):
    app = App()
    app.run()

if __name__ == "__main__":
    main(sys.argv[1:])