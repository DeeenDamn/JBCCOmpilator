import myparser
import os
import sys


# solomatin.cs.vsu.ru@gmail.com
def main():
    with open('{}.txt'.format(sys.argv[1]), 'r') as file:
        prog = myparser.parse(file.read())

    '''prog = myparser.parse(
            public class A
    {   
        public static int factorial(int n){
			int res = n;
			if (n > 1){
				res *= factorial(n-1);
				}
			return res;
		}
        
        public static void main(string[] argc){
            int n = factorial(5);	
            Console.WriteLine(n);
        }
    }
    )'''
    #print(sys.argv[1])
    print(*prog.tree, sep=os.linesep)



if __name__ == "__main__":
    main()

