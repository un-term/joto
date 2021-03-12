#!/usr/bin/env python

# breakpoint()
# from joto import JotoSQLiteDB

import joto

def main():


    db_path = "joto.db"
    src_dir = "ingest_images/"
    dst_dir = "images/compressed/"
    achv_dir = "images/original"
    size = "1000x1000"

    sqlite_db = joto.JotoSQLiteDB(db_path)
    images_manage = joto.ImagesManage(size, src_dir, dst_dir, achv_dir)

    joto = joto.Joto(sqlite_db,images_manage)
    joto.check_requirements()
    joto.scan_for_and_add_images_with_text()

if __name__ == "__main__":
    main()
