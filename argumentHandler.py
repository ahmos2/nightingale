import argparse
parser=argparse.ArgumentParser()
parser.add_argument("--privatekey", help="Key to verify signatures", default="Never gonna give you up")
parser.add_argument("--signature", help="Initial signature", default="Never gonna let you down")
parser.add_argument("--certkey", help="Private key for the server certificate", default="/home/pi/certificate/remote1.key")
parser.add_argument("--certificate",help="Server certificate", default="/home/pi/certificate/remote1.crt")
parser.add_argument("--certchain",  help="Certs for root and intermediate CAs", default="/home/pi/certificate/rootCA.pem")
args=parser.parse_args()