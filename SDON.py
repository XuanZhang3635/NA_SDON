from fabric import Connection
import tkinter as tk
from tkinter import ttk
import json

# Parameters of connecting to the remote host
remote_host = '10.79.23.42'
remote_user = 'team1'
remote_password = 'Team123.'
remote_port = 22  # Default port 22

connection = Connection(
    host=remote_host,
    user=remote_user,
    connect_kwargs={"password": remote_password},
    port=remote_port,
)

id1 = None
id2 = None
class_name = None
rate = None
name = None

def create_service(ctx,id1,id2,class_name,rate,name):
    with ctx.cd('NA-projects'):
        # auth
        ctx.run('./script-auth.sh', warn=True)
        print("parameters: ",id1,id2,class_name,rate,name)
        json_data = {
                    "className": "Connection",
                    "connEndPoints": [{
                    "className": "ConnEndPoint",
                    "ltp": {
                    "className": "Ltp",
                    "id": id1
                    },
                    "endType": "source"
                    }, {
                    "className": "ConnEndPoint",
                    "ltp": {
                    "className": "Ltp",
                    "id": id2
                    },
                    "endType": "sink"
                    }
                    ],
                    "routingCriteria": "byLength",
                    "sncpInfo": {"holdOffTime": 0, "revertive": True,"sncpType": "sncp_i", "wtrTime": 300 },
                    "connLps": [{
                    "className": class_name,
                    "rate": rate
                    }
                    ],
                    "configurationState": "implemented",
                    "hierarchicalLevel": "service",
                    "name": name,
                    "protection": False
                }

        cmd = 'curl -k -b cookie.curl -XPOST -H "Content-Type: application/json" -d '+ f"'{json.dumps(json_data)}'" +' "https://10.79.23.42/onc/connection"'
        print("command:",cmd)
        ctx.run(cmd)

def delete_service(ctx,id_delete):
    with ctx.cd('NA-projects'):
        # auth
        ctx.run('./script-auth.sh', warn=True)
        url = "https://10.79.23.42/onc/connection/" + id_delete 
        cmd = 'curl -k -b cookie.curl -XDELETE ' + f"'{url}'"
        
        ctx.run(cmd)

def get_service_connection(ctx):

    with ctx.cd('NA-projects'):
        # auth
        ctx.run('./script-auth.sh', warn=True)
        result = ctx.run('curl -k -b cookie.curl "https://10.79.23.42/onc/connection?hierarchicalLevel==service&view(connEndPoints.ltp.ne)"', warn=True)
        print(result.stdout)


def get_ltps(ctx,ne_name):
    with ctx.cd('NA-projects'):
        # auth
        ctx.run('./script-auth.sh', warn=True)
        url = "https://10.79.23.42/onc/ltp?ltpType==physical&ne.name==" + ne_name + "&select(id,name)"
        print(url)
        result = ctx.run('curl -k -b cookie.curl ' + f"'{url}'" , warn=True)
        # debug
        print("Output:", result.stdout)
        return result

def input_source(event):
    global id1
    id1 = entry_source.get()
    print("The input source is ", id1)

def input_sink(event):
    global id2
    id2 = entry_sink.get()
    print("The input sink is ", id2)

def input_class_name(event):
    global class_name
    class_name = entry_class_name.get()
    print("class name is ",class_name)

def input_rate(event):
    global rate
    rate = entry_rate.get()
    print("rate is ",rate)

def input_name(event):
    global name
    name = entry_name.get()
    print("name is ",name)

def input_delete(event):
    global id_delete
    id_delete = entry_delete.get()
    print("The id of the connection to be deleted is ",id_delete)

def ne_select(event):
    global name
    name = combo.get()

if __name__ == '__main__':
    
    ################# draw GUI ##################

    root = tk.Tk()
    root.title("SDON")
    root.geometry("500x400")
    root.grid_rowconfigure(0, minsize=20) 

    label_from = tk.Label(root, text="source(Press Enter key to confirm):")
    label_from.grid(row=1, column=0)
    entry_source = tk.Entry(root)
    entry_source.grid(row=1, column=1)
    entry_source.bind("<Return>", input_source)

    label_to = tk.Label(root, text="sink(Press Enter key to confirm):")
    label_to.grid(row=2, column=0)
    entry_sink = tk.Entry(root)
    entry_sink.grid(row=2, column=1)
    entry_sink.bind("<Return>", input_sink)
    
    label_class_name = tk.Label(root, text="className(Press Enter key to confirm): ")
    label_class_name.grid(row=3, column=0)
    entry_class_name = tk.Entry(root)
    entry_class_name.grid(row=3, column=1)
    entry_class_name.bind("<Return>", input_class_name)

    label_rate = tk.Label(root, text="rate(Press Enter key to confirm): ")
    label_rate.grid(row=4, column=0)
    entry_rate = tk.Entry(root)
    entry_rate.grid(row=4, column=1)
    entry_rate.bind("<Return>", input_rate)

    label_name = tk.Label(root, text="name(Press Enter key to confirm): ")
    label_name.grid(row=5, column=0)
    entry_name = tk.Entry(root)
    entry_name.grid(row=5, column=1)
    entry_name.bind("<Return>", input_name)

    button_create = tk.Button(root, text="Create", command=lambda:create_service(connection,id1,id2,class_name,rate,name))
    button_create.grid(row=6,column=1)


    label_delete = tk.Label(root, text="delete service(Press Enter key to confirm):")
    label_delete.grid(row=8, column=0)
    entry_delete = tk.Entry(root)
    entry_delete.grid(row=8, column=1)
    entry_delete.bind("<Return>", input_delete)

    button_delete = tk.Button(root, text="Delete", command=lambda:delete_service(connection,id_delete))
    button_delete.grid(row=9,column=1)

    root.grid_rowconfigure(11, minsize=60)
    root.grid_rowconfigure(12, minsize=60)
    combo_var = tk.StringVar()
    combo = ttk.Combobox(root, textvariable=combo_var)
    combo['values'] = ('team1-NE-1','team1-NE-2')
    combo.grid(row=12, column=0)
    result_label = tk.Label(root, text="")
    combo.bind('<<ComboboxSelected>>', ne_select)
    button_find_ltps = tk.Button(root, text="Find ltp", command=lambda:get_ltps(connection,name))
    button_find_ltps.grid(row=12,column=1)

    button_find_connection = tk.Button(root, text="Find connection", command=lambda:get_service_connection(connection))
    button_find_connection.grid(row=11,column=0)
    
    root.mainloop()
