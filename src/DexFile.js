import {xu} from "xu";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";

export class DexFile
{
	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static async create(o)
	{
		const dexFile = new this({allowNew : true});
		dexFile.rel = typeof o==="string" ? path.basename(o) : o.subPath;
		dexFile.root = path.join(typeof o==="string" ? path.dirname(o) : path.resolve(o.root));
		dexFile.absolute = path.join(dexFile.root, dexFile.rel);

		const pathInfo = path.parse(dexFile.absolute);
		["base", "dir", "name", "ext"].forEach(n => { dexFile[n] = pathInfo[n]; });

		const fileInfo = await Deno.lstat(dexFile.absolute);
		["isFile", "isDirectory", "isSymlink", "size"].forEach(n => { dexFile[n] = fileInfo[n]; });
		dexFile.ts = fileInfo.mtime;	// eslint-disable-line require-atomic-updates

		const periodLoc = dexFile.base.indexOf(".");
		dexFile.pre = periodLoc===-1 ? "" : dexFile.base.substring(0, periodLoc+1);
		dexFile.preName = dexFile.base.substring(dexFile.pre.length);

		return dexFile;
	}

	// creates a copy of this
	clone()
	{
		const dexFile = new DexFile({allowNew : true});
		Object.assign(dexFile, this);
		return dexFile;
	}

	// changes the root of this file to something else
	changeRoot(newRoot)
	{
		this.root = path.resolve(newRoot);
		this.absolute = path.join(newRoot, this.rel);
		this.dir = path.dirname(this.absolute);
		return this;
	}
}
