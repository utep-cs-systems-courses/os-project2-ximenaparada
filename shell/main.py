#! /usr/bin/env python3
import os, sys, re

def execCommand(args):
    for dir in re.split(":", os.environ['PATH']):   #Traverse path dir
        program = "%s/%s" % (dir, args[0])        
        try:
            os.execve(program, args, os.environ)    #try exec prog
        except FileNotFoundError:
            os.write(2, ("%s: command not found\n" % args[0]).encode())
            pass
        os.write(2, ("%s: program terminated with exit code 1\n" % args[0]).encode())
        sys.exit(1) #terminate w/error

def redirectOutput(args):
    leftCommand = args[args.index(">") + 1:]
    os.close(1)
    sys.stdout = os.open(leftCommand[0], os.O_RDWR)
    os.set_inheritable(1, True)
    return args[:args.index(">")]
    

def redirectInput(args):
    rightCommand = args[args.index("<") + 1:]
    os.close(0)
    sys.stdin = os.open(rightCommand[0], os.O_RDONLY)
    os.set_inheritable(0, True)
    return args[:args.index("<")]

def pipe(args):
    leftCommand = args[:args.index("|")]
    rightCommand = args[args.index("|") + 1]
    pipeR, pipeW = os.pipe()    # DIfferent pipe()
    rc = os.fork()
    if rc < 0:
        print("error!!!     view fork")
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = os.dup(pipeW)
        os.set_inheritable(1, True)
        for fd in (pipeR, pipeW):
            os.close(fd)
        execCommand(leftCommand)
    else:
        os.close(0)
        sys.stdin = os.dup(pipeR)
        os.set_inheritable(0, True)
        for fd in (pipeR, pipeW):
            os.close(fd)
        execCommand(rightCommand)

def exitShell(args):
    if args[0] == "exit":
        sys.exit(0)
    
def cdCommand(args):
    if args[0] == "cd":
        temp = os.getcwd() + args[1]
        os.chdir(os.getcwd() + "/" + args[1])
        return True
    return False

def checkPS1(args):
    if args[0] == "PS1":
        return True
    return False
        

if __name__ == '__main__':
    ps1 = "$"
    while True:
        args = input(os.getcwd() + ps1 + " ")
        args = args.split(" ")

        if len(args) == 2 :
            if cdCommand(args):
                continue
            if checkPS1(args): 
                ps1 = args[1]
                continue
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            exitShell(args)
            if "|" in args:
                pipe(args)
            if ">" in args:
                args = redirectOutput(args)
                execCommand(args)
            elif "<" in args:
                args = redirectInput(args)
                execCommand(args)
            else:
                execCommand(args)
        else:
            exitShell(args)
            os.wait()