#!/usr/bin/env python3

# Modified from the SAMPL Challenges site

import argparse
import re
import os
import sys
import string
import yaml  # depends on PyYAML
from collections import OrderedDict

page_titles = OrderedDict()

# Pages
def get_md_pages(path='_docpages'):
    pages = []
    for p in os.listdir(path):
        if p.endswith('.md'):
            pages.append(os.path.join(path, p))
    return pages


def make_link_from_heading(heading):
    translator = str.maketrans('', '', string.punctuation)
    translator.pop(45)  # don't replace '-'
    return heading.translate(translator).lower().replace(' ', '-')


def get_subtoc(headings, level, file_location):
    lines = []
    for h in headings:
        lines.append(level*2*' ' + '- title: ' + h['title'])
        lines.append(level*2*' ' + '  url: ' + file_location + h['ref'])
        if h['sub']:
            lines.append(level*2*' ' + '  children:')
            lines.extend(get_subtoc(h['sub'], level + 1, file_location))
    return lines

def get_header(lines, pattern='---'):
    n_pattern = 0
    header = []
    while lines:
        line = lines.pop(0)
        if line == pattern:
            n_pattern += 1
        if n_pattern == 1:
            header.append(line)
        elif n_pattern == 2:
            return header, lines
    return [], []

def create_toc(file):
    find_heading = re.compile('^(#+) (.*)')
    headings = []
    with open(file, 'r') as f:
        file_contents = [x.strip('\n') for x in f.readlines()]
    
    header, content = get_header(file_contents)
    header_string = '\n'.join(header)
    front_matter = yaml.load(header_string)

    rewrite_frontmatter = False
    base_filename = os.path.basename(file).replace('.md', '')
    title = ''
    print(file, front_matter, header, content, '\n\n\n')
    if 'title' in front_matter:
        title = front_matter['title']

    if 'permalink' in front_matter:
        permalink = front_matter['permalink']
    else:
        permalink = '/docpages/' + base_filename + '/'
        rewrite_frontmatter = True
    
    page_titles[title] = permalink
    
    if 'sidebar' not in front_matter or 'nav' not in front_matter['sidebar']:
        nav = os.path.join('pages', base_filename)
        header = [x for x in header if not x.startswith('sidebar')]
        header.append('sidebar:')
        header.append('  nav: ' + nav)
        rewrite_frontmatter = True
    else:
        nav = front_matter['sidebar']['nav']
    
    if rewrite_frontmatter:
        with open(file, 'w') as f:
            # f.write('---\n')
            f.write('\n'.join(header))
            f.write('\n---\n')
            f.write('\n'.join(content))
            f.write('')

    headings.append({'title': title,
                     'ref': '#',
                     'sub': []})

    # Read remaining file
    for line in content:
        match = find_heading.match(line)
        if match is None:
            continue
        heading_level = len(match.group(1))
        heading = match.group(2).strip()
        heading_ref = '#' + make_link_from_heading(heading)
        if heading_level == 1:
            headings.append({'title': heading,
                             'ref': heading_ref,
                             'sub': []})
        else:
            parent = headings
            for n in range(heading_level - 1):
                if len(parent) == 0:
                    parent.append({'title': '',
                                   'ref': '#',
                                   'sub': []})
                parent = parent[-1]['sub']
            parent.append({'title': heading,
                           'ref': heading_ref,
                           'sub': []})

    lines = ['', nav+':'] + get_subtoc(headings, 1, permalink)
    return lines



def main(args):
    # argparse might be overkill, but at least we have a little help file
    parser = argparse.ArgumentParser(description=('Generate YAML table of content ' +
                                                  'from markdown files located in _pages' +
                                                  'Output of this script should be redirected to ' +
                                                  '_data/navigation.yml'),
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-o', dest='destination', default='_data/navigation.yml', required=False)

    parsed = parser.parse_args(args)

    toc_lines = []

    # print sidebar navigation for files
    pages = get_md_pages()
    for file in pages:
        toc_lines.extend(create_toc(file))
    
    nav_lines = ['main:']
    for title, url in page_titles.items():
        nav_lines.append('  - title: ' + title)
        nav_lines.append('    url: ' + url + '/')
    
    nav_lines += toc_lines

    with open(parsed.destination, 'w') as f:
        f.write('\n'.join(nav_lines))
    print('Wrote data to ' + parsed.destination)



if __name__ == "__main__":
    main(sys.argv[1:])
