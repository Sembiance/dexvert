import {xu, fg} from "xu";
import {fileUtil} from "xutil";
import {path, assertStrictEquals} from "std";
import {validateClass} from "./validate.js";

export class Server
{
	static servers = null;
	serverid = this.constructor.name;
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	static create()
	{
		const server = new this();

		validateClass(server, {
			// required
			serverid : {type : "string", required : true}, 	// automatically set to the constructor name
			start    : {type : "function", length : 0, required : true},
			status   : {type : "function", length : 0, required : true},
			stop     : {type : "function", length : 0, required : true}
		});

		return server;
	}

	log(strs, ...vals)
	{
		xu.log([`${xu.colon(fg.peach(this.constructor.name))}${strs[0]}`, ...strs.slice(1)], ...vals);
	}

	// loads all src/server/*.js files from disk as Server objects. These are cached in the static this.servers cache
	static async loadServers()
	{
		if(this.servers!==null)
		{
			await xu.waitUntil(() => Object.isObject(this.servers));
			return this.servers;
		}
		
		this.servers = false;
		const servers = {};

		for(const serverFilePath of await fileUtil.tree(path.join(xu.dirname(import.meta), "server"), {nodir : true, regex : /.+\.js$/}))
		{
			const serverModule = await import(serverFilePath);
			const serverid = Object.keys(serverModule)[0];

			// class name must match filename
			assertStrictEquals(serverid, path.basename(serverFilePath, ".js"), `server file [${serverFilePath}] does not have a matching class name [${serverid}]`);

			// check for duplicates
			if(servers[serverid])
				throw new Error(`server ${fg.peach(serverid)} at ${serverFilePath} is a duplicate of ${servers[serverid]}`);

			// create the class and validate it
			servers[serverid] = serverModule[serverid].create();
			if(!(servers[serverid] instanceof this))
				throw new Error(`server ${fg.peach(serverid)} at [${serverFilePath}] is not of type Server`);
		}
		
		this.servers = servers;
		return this.servers;
	}
}
