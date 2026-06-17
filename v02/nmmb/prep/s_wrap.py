import re
import sys

def wrap_line(line):
    line = line.rstrip('\n')
    # If line is structural but contains Sanskrit parts
    if line.startswith(';c{'):
        return re.sub(r';c\{(.*)\}', r';c{<s>\1</s>}', line)
    if line.startswith(';k{'):
        return re.sub(r';k\{(.*)\}', r';k{<s>\1</s>}', line)
    if '<eid>' in line and '<syns>' in line:
        # handle <eid>n<syns>word1,word2
        m = re.search(r'(<eid>.*?<syns>)(.*)', line)
        if m:
            return m.group(1) + '<s>' + m.group(2) + '</s>'
    
    # If line is entirely structural
    if line.startswith(';') or line.startswith('<') or line.startswith('---'):
        return line
    
    # If line is empty or whitespace
    if not line.strip():
        return line
    
    # Otherwise wrap the whole line
    return '<s>' + line + '</s>'

def process(filein, fileout):
    with open(filein, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    content_reached = False
    for line in lines:
        if line.startswith(';CONTENT'):
            content_reached = True
            new_lines.append(line.rstrip('\n'))
            continue
        
        if content_reached:
            new_lines.append(wrap_line(line))
        else:
            new_lines.append(line.rstrip('\n'))
            
    with open(fileout, 'w', encoding='utf-8') as f:
        for line in new_lines:
            f.write(line + '\n')

if __name__ == '__main__':
    filein = sys.argv[1]
    fileout = sys.argv[2]
    process(filein, fileout)
