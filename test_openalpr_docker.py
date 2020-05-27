import subprocess
def test_openalpr():
    # txt = os.system("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu MY02ZR0.jpg | sed -n '2p'"))
    res = subprocess.getstatusoutput("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu MY02ZR0.jpg | sed -n '2p'")
    print(res)
    record = res[1].split("\t confidence: ")
    print(record)
    # return plate_str, confidence
    return record[0], record[1]

if __name__ == '__main__':
    test_openalpr()