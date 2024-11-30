with open('requirements.txt') as f, open('output.txt', 'w') as out:
    for line in f:
        package = line.split('==')[0]
        out.write(package + '\n')