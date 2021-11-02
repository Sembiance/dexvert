import {xu} from "xu";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";

export class DexFile
{
	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static async create(o)
	{
		const dexFile = new this({allowNew : true});
		dexFile.root = path.join(typeof o==="string" ? (o.startsWith("/") ? path.dirname(o) : Deno.cwd()) : path.resolve(o.root));
		dexFile.rel = typeof o==="string" ? (o.startsWith("/") ? path.basename(o) : o) : o.subPath;
		dexFile.absolute = path.join(dexFile.root, dexFile.rel);

		const pathInfo = path.parse(dexFile.absolute);
		["base", "dir", "name", "ext"].forEach(n => { dexFile[n] = pathInfo[n]; });

		const fileInfo = await Deno.lstat(dexFile.absolute);
		["isFile", "isDirectory", "isSymlink", "size"].forEach(n => { dexFile[n] = fileInfo[n]; });
		dexFile.ts = fileInfo.mtime;	// eslint-disable-line require-atomic-updates

		const periodLoc = dexFile.base.indexOf(".");
		dexFile.preExt = periodLoc===-1 ? "" : `.${dexFile.base.substring(0, periodLoc)}`;
		dexFile.preName = dexFile.base.substring(dexFile.preExt.length);

		dexFile.transformed = Object.isObject(o) && o.transformed;
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
