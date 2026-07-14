from core.assistant import Jarvis


def main():

    jarvis = Jarvis()


    try:

        jarvis.initialize()

        jarvis.run()


    except KeyboardInterrupt:

        print(
            "\n退出 Jarvis..."
        )


    finally:

        jarvis.shutdown()



if __name__ == "__main__":

    main()