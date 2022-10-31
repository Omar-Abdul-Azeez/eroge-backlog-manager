import json
from datetime import date

import requests


def dump(full_backup):
    if full_backup:
        enm = ['Unknown', 'Pending', 'Obtained', 'On loan', 'Deleted']
        req = {
            "fields": "id, labels.label, started, finished, notes, vn{title, alttitle, image{id, url}}, releases{list_status, id, title, alttitle, languages.lang, platforms, vns.id, patch, released, notes}"
        }
    else:
        req = {
            "filters": ["or", ["label", "=", "10"], ["label", "=", "11"], ["label", "=", "13"]],
            "fields": "id, vn{title, alttitle, image{id, url}}, releases{list_status, id, title, alttitle, platforms, vns.id, patch}"
        }
    req['user'] = 'u192153'
    req['results'] = 100
    i = 0
    dmp = dict()
    while True:
        i += 1
        req['page'] = i
        r = requests.post("https://api.vndb.org/kana/ulist", json=req)
        r = r.json()
        for vn in r['results']:
            if full_backup:
                lbls = []
                for lbl in vn['labels']:
                    lbls.append(lbl['label'])
                vn['labels'] = lbls
            title = ''
            if vn['vn']['alttitle'] == '':
                title = vn['vn']['title']
            else:
                title = vn['vn']['alttitle']
            img = vn['vn']['image']
            del vn['vn']
            vn['title'] = title
            vn['cover'] = img
            ind = 0
            while ind < len(vn['releases']):
                if vn['releases'][ind]['list_status'] != 2 and not full_backup:
                    del vn['releases'][ind]
                else:
                    if full_backup:
                        langs = []
                        for lang in vn['releases'][ind]['languages']:
                            langs.append(lang['lang'])
                        vn['releases'][ind]['languages'] = langs
                        vn['releases'][ind]['status'] = enm[vn['releases'][ind]['list_status']]
                    del vn['releases'][ind]['list_status']
                    if vn['releases'][ind]['alttitle'] == '':
                        del vn['releases'][ind]['alttitle']
                    else:
                        vn['releases'][ind]['title'] = vn['releases'][ind]['alttitle']
                        del vn['releases'][ind]['alttitle']
                    vns = []
                    for v in vn['releases'][ind]['vns']:
                        vns.append(v['id'])
                    vn['releases'][ind]['vns'] = vns
                    ind += 1
            vid = vn['id']
            del vn['id']
            dmp[vid] = vn
        if not r['more']:
            break
    return dmp


def write_dump(full_backup, dmp=None):
    if not dmp:
        dmp = dump(full_backup)
    with open(f'vndb{"-full_backup" if full_backup else ""}-{date.today().strftime("%Y-%m-%d")}.json', 'w',
              encoding='utf-8') as f:
        json.dump(dmp, f, ensure_ascii=False)


def main():
    try:
        full_backup = bool(input('Dump entire userlist?\n>'))
        write_dump(full_backup)
    except Exception as e:
        print(e)
        input()


if __name__ == '__main__':
    main()
