def Command_handler(command):
    print(command)
    content = command.split()
    if len(content) > 1:
        if content[0] == "$title":
            status, title, X, Y = Process_reserve(content)
            return status, title, X, Y
        if content[0] == "$release":
            status, title, X, Y = Process_release(content)
            return status, title, X, Y
        else:
            return 0, "", "", ""
    else:
        return 0 , "", "", ""


def Process_reserve(content):
    if len(content) == 4:

        X = content[2].split(':')
        Y = content[3].split(':')
        return 1,content[1],X[1],Y[1]

    else:
        return 0,"","",""
    

def Process_release(content):

    if len(content) == 2:

        if content[1] == "duke":
            return 2, "duke", "", ""
        elif content[1] == "architect":
            return 2, "architect", "", ""
        elif content[1] == "scientist":
            return 2, "scientist", "", ""
        elif content[1] == "justice":
            return 2, "justice", "", ""
        else: 
            return 0, "", "", ""
        
    else: 
        return 0