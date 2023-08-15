def main(argv):
    # Change to script directory
    # abspath = os.path.abspath(sys.argv[0])
    # dname = os.path.dirname(abspath)
    # os.chdir(dname)

    # Specify format type here

    options, arguments = getopt.getopt(sys.argv[1:] , "" ,
        ["help","config-file=","scan=","image-path=", "text", "create-req", "delete-req","delete-entry=","delete-last-entry", "create-content"])

    # Required
    config_file_status = False
    for option, argument in options:
        if option == "--config-file":
            if os.path.isfile(argument):
                json_config = JsonConfig(argument)
                sqlite_db = JotoSQLiteDB(json_config.sqlite_db_path)
                images_manage = ImagesManage(json_config.image_size, json_config.original_image_dirpath, json_config.compressed_image_dirpath)
                text_input = TextInput()
                html = HTML("template.html", json_config.html_output_path, json_config.compressed_image_dirpath)
                joto_obj = Joto(sqlite_db, images_manage, text_input, html)
                config_file_status = True

    if not config_file_status:
        raise Exception("config file required") 

    for option, argument in options:
        if option == "--scan":
            if os.path.exists(argument):
                print("Scan: ", argument)
                joto_obj.check_req()
                joto_obj.scan_for_and_add_images_with_text(argument)
                joto_obj.create_content()
                joto_obj.write_content()
        elif option == "--image-path":
            if os.path.isfile(argument):
                print("Adding image by path")
                joto_obj.check_req()
                joto_obj.add_image_from_path(argument)
                joto_obj.create_content()
                joto_obj.write_content()
            else:
                print("wrong path")
        elif option == "--text":
            joto_obj.check_req()
            joto_obj.add_text_only()
            joto_obj.create_content()
            joto_obj.write_content()
        elif option == "--create-content":
            joto_obj.create_content()
            joto_obj.write_content()
        elif option == "--create-req":
            joto_obj.create_req()
            joto_obj.check_req()
        elif option == "--delete-req":
            joto_obj.delete_req()
        elif option == "--delete-entry":
            joto_obj.delete_entry(argument)
        elif option == "--delete-last-entry":
            joto_obj.delete_last_entry()
        elif option == "--help":
            print("Options:","--config-file","--scan","--image-path","--text","--create-content","--create-req","--delete-req","--delete-last-entry")

 
if __name__ == "__main__":
   main(sys.argv[1:])
