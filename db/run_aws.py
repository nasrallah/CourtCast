#!/usr/bin/env python
from app import app

def main():
    app.run('0.0.0.0', port=80, debug = False)



if __name__ == '__main__':
    main()