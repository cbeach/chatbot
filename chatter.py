import aiml


class Chatter:
    botList = [
    "alice"]
    k = None

    def __init__(self):
        self.k = aiml.Kernel()
        pass

    def load_bot(self, bot):
        list_of_files = open("./" + bot + "/files")
        line = list_of_files.readline()
        files = line.split(" ")
        for i in files:
            i = "./" + bot + "/" + i
            print("loading: " + i)
            self.k.learn(i)
            i = list_of_files.readline()
        
    def start_bot_loop(self):
        self.k.respond("load aiml b")
        while True:
            print(self.k.respond(raw_input("> ")))

    def get_reply(self, msg):
        return self.k.respond(msg)

def main():
    chat = Chatter()
    chat.load_bot("alice")
    chat.start_bot_loop()

if __name__ == "__main__":
    main()
        
        

