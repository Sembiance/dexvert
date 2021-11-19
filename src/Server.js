import {xu, fg} from "xu";
import {validateClass} from "./validate.js";

export class Server
{
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
}
