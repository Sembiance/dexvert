import {xu} from "xu";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";

export class DexFile
{
	// builder to get around the fact that constructors can't be async
	static async create(o)
	{
		const dexFile = new this();
		dexFile.root = path.join(typeof o==="string" ? (o.startsWith("/") ? path.dirname(o) : Deno.cwd()) : path.resolve(o.root));
		dexFile.rel = typeof o==="string" ? (o.startsWith("/") ? path.basename(o) : o) : o.subPath;
		dexFile.absolute = path.join(dexFile.root, dexFile.rel);
		dexFile.transformed = Object.isObject(o) && o.transformed;

		dexFile.calcProps();

		const fileInfo = await Deno.lstat(dexFile.absolute);
		["isFile", "isDirectory", "isSymlink", "size"].forEach(n => { dexFile[n] = fileInfo[n]; });
		dexFile.ts = fileInfo.mtime.getTime();	// eslint-disable-line require-atomic-updates

		return dexFile;
	}

	calcProps()
	{
		const pathInfo = path.parse(this.absolute);
		["base", "dir", "name", "ext"].forEach(n => { this[n] = pathInfo[n]; });

		const periodLoc = this.base.indexOf(".");
		this.preExt = periodLoc===-1 ? "" : `.${this.base.substring(0, periodLoc)}`;
		this.preName = this.base.substring(this.preExt.length);
	}

	// changes the root of this file to something else
	changeRoot(newRoot)
	{
		this.root = path.resolve(newRoot);
		this.absolute = path.join(newRoot, this.rel);
		this.dir = path.dirname(this.absolute);
		return this;
	}

	// renames this file to the newFilename
	async rename(newFilename)
	{
		const newAbsolute = path.join(this.dir, newFilename);
		await Deno.rename(this.absolute, newAbsolute);
		this.absolute = newAbsolute;
		this.rel = this.rel.includes("/") ? path.join(path.dirname(this.rel), newFilename) : newFilename;
		this.calcProps();
	}

	// creates a copy of this
	clone()
	{
		const dexFile = new DexFile();
		Object.assign(dexFile, this);
		return dexFile;
	}

	// converts this to a serilizable object
	serialize()
	{
		return Object.fromEntries(Object.entries(this));
	}

	// deserializes an object into a Dexfile
	static deserialize(o)
	{
		const dexfile = new this();
		Object.assign(dexfile, o);
		return dexfile;
	}

	// returns a pretty string representing this file
	pretty(prefix="")
	{
		const r = [prefix];
		r.push(this.isDirectory ? xu.cf.fg.magenta("D") : (this.isSymlink ? xu.cf.fg.cyan("L") : xu.cf.fg.fogGray("F")));
		r.push(` ${xu.cf.fg.white(this.size.bytesToSize().padStart(6, " "))}`);
		r.push(` ${xu.cf.fg.yellow(this.root)}${xu.cf.fg.cyan("/")}${xu.cf.fg.yellowDim(this.rel)}`);
		if(this.transformed)
			r.push(` ${xu.cf.fg.peach("transformed")}`);
		return r.join("");
	}
}
