import {xu, fg} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";

export class DexFile
{
	// builder to get around the fact that constructors can't be async
	static async create(o)
	{
		const dexFile = new this();
		dexFile.root = path.join(typeof o==="string" ? (o.startsWith("/") ? path.dirname(o) : Deno.cwd()) : path.resolve(o.root));
		dexFile.rel = typeof o==="string" ? (o.startsWith("/") ? path.basename(o) : o) : (o.absolute ? path.relative(dexFile.root, o.absolute) : o.rel);
		dexFile.absolute = path.join(dexFile.root, dexFile.rel);

		dexFile.calcProps();
		await dexFile.calcStats();

		return dexFile;
	}

	async calcStats()
	{
		const fileInfo = await Deno.lstat(this.absolute).catch(() => {});	// we used to check if it exists first, but it could disappear between checking and lstat, so now we just try to lstat and fail gracefully
		if(!fileInfo)
			return;
		["isFile", "isDirectory", "isSymlink", "size"].forEach(n => { this[n] = fileInfo[n]; });
		this.ts = fileInfo.mtime.getTime();
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
	changeRoot(newRoot, {keepRel, relativeFrom}={})
	{
		this.root = path.resolve(newRoot);
		if(!keepRel)
			this.rel = path.relative(newRoot, this.absolute);

		this.absolute = path.join(newRoot, this.rel);
		this.dir = path.dirname(this.absolute);

		if(relativeFrom)
			this.rel = path.relative(relativeFrom, this.absolute);

		return this;
	}

	// renames this file to the newFilename
	async rename(newFilename, {autoRename, replaceExisting}={})
	{
		if(newFilename===this.base)
			return;

		let newAbsolute = path.join(this.dir, newFilename);
		if(!replaceExisting && await fileUtil.exists(newAbsolute))
		{
			if(!autoRename)
				throw new Error(`Dexfile.rename asked to rename ${this.absolute} to ${newAbsolute} but that already exists and autoRename wasn't set`);
			
			let i=0;
			do
				newAbsolute = path.join(this.dir, `${path.basename(newFilename, path.extname(newFilename))}_${i++}${path.extname(newFilename)}`);
			while(await fileUtil.exists(newAbsolute));
		}

		await Deno.rename(this.absolute, newAbsolute);
		this.absolute = newAbsolute;
		this.rel = this.rel.includes("/") ? path.join(path.dirname(this.rel), newFilename) : newFilename;
		this.calcProps();
	}

	// moves a file up 1 or more directories
	async moveUp(levels=1)
	{
		this.dir = path.resolve(this.dir, ...Array(levels).fill(".."));
		const newAbsolute = path.join(this.dir, this.base);
		this.rel = path.relative(this.root, newAbsolute);
		await Deno.rename(this.absolute, newAbsolute);
		this.absolute = newAbsolute;
	}

	// creates a copy of this
	clone()
	{
		const dexFile = new DexFile();
		Object.assign(dexFile, this);
		return dexFile;
	}

	// sets the timestamp for this file
	async setTS(newTS)
	{
		this.ts = newTS;
		await Deno.utime(this.absolute, Math.floor(this.ts/xu.SECOND), Math.floor(this.ts/xu.SECOND));
	}

	// converts this to a serilizable object
	serialize()
	{
		return Object.fromEntries(Object.entries(this));
	}

	// returns a pretty string representing this file
	pretty(prefix="")
	{
		const r = [prefix];
		r.push(this.isDirectory ? fg.violet("D") : (this.isSymlink ? fg.cyan("L") : fg.fogGray("F")));
		r.push(` ${fg.white((this.isFile ? this.size.bytesToSize() : "").padStart(6, " "))}`);
		r.push(` ${fg.magenta(this.root)}${fg.cyan("/")}${fg.magenta(this.rel)}`);
		return r.join("");
	}
}
