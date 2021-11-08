import {xu} from "xu";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import {runUtil} from "xutil";
import {DexFile} from "./DexFile.js";

export class FileSet
{
	root = null;
	files = {};

	// builder to get around the fact that constructors can't be async
	static async create(o)
	{
		if(!o)
			return null;

		const fileSet = new this();

		function getRoot(v)
		{
			return (v instanceof DexFile ? v.root : (v.startsWith("/") ? path.dirname(v) : Deno.cwd()));
		}

		if(typeof o==="string")
		{
			// a string, assume we just have a single main file, absolute path
			fileSet.root = getRoot(o);
			await fileSet.add("main", path.basename(o));
		}
		else if(o instanceof DexFile)
		{
			// a single DexFile, assume it's a main file
			fileSet.root = o.root;
			await fileSet.add("main", o);
		}
		else if(Array.isArray(o))
		{
			// an array, assume it's an array of main files
			fileSet.root = o.map(getRoot).sortMulti([v => v.length])[0];
			for(const v of o)
				await fileSet.add("main", path.relative(fileSet.root, v));
		}
		else if(!Object.hasOwn(o, "root"))
		{
			// an object without a root
			fileSet.root = Object.values(o).flatMap(v => Array.force(v)).map(getRoot).sortMulti([v => v.length])[0];
			for(const [type, files] of Object.entries(o))
			{
				for(const file of files)
					await fileSet.add(type, file);
			}
		}
		else
		{
			fileSet.root = path.resolve(o.root);
			for(const [type, files] of Object.entries(o.files || {}))
			{
				for(const file of files)
					await fileSet.add(type, file);
			}
		}

		return fileSet;
	}

	// rsync copies all files to targetRoot and returns a FileSet for the new root
	async rsyncTo(targetRoot, {type}={})
	{
		for(const file of (type ? this.files[type] : this.all))
		{
			if(file.rel.includes("/"))
				await Deno.mkdir(path.join(targetRoot, path.dirname(file.rel)), {recursive : true});
			await runUtil.run("rsync", ["-aL", path.join(this.root, file.rel), path.join(targetRoot, file.rel)]);
		}

		return this.clone().changeRoot(targetRoot);
	}

	async addAll(type, files)
	{
		for(const file of files)
			await this.add(type, file);
		
		// Doing this would be faster probably, but would yield files being added potentially out of order, which might be important to maintain
		//await Promise.all(files.map(file => this.add(type, file)));
	}

	// adds the given file of type type
	async add(_type, _o)
	{
		const type = typeof _o==="undefined" ? "main" : _type;
		const o = typeof _o==="undefined" ? _type : _o;

		if(!this.files[type])
			this.files[type] = [];

		if(o instanceof DexFile)
		{
			if(o.root!==this.root)
				throw new Error(`Can't add dex file ${o.pretty()} due to root not matching FileSet root: ${this.root}`);
			this.files[type].push(o);
		}
		else if(typeof o==="string")
		{
			this.files[type].push(await DexFile.create({root : this.root, subPath : o.startsWith("/") ? path.relative(this.root, o) : o}));
		}
		else
		{
			throw new TypeError(`Can't add file ${o} to FileSet due to being an unknown type ${typeof o}`);
		}
	}

	// changes the root location of this FileSet and the DexFiles within it
	changeRoot(newRoot)
	{
		this.root = path.resolve(newRoot);
		for(const file of this.all)
			file.changeRoot(newRoot);
		
		return this;
	}

	// creates a copy of this
	clone()
	{
		const fileSet = new FileSet();
		fileSet.root = this.root;
		fileSet.files = Object.fromEntries(Object.entries(this.files).map(([k, subFiles]) => ([k, subFiles.map(subFile => subFile.clone())])));
		return fileSet;
	}

	// converts this to a serilizable object
	serialize()
	{
		const o = {};
		o.root = this.root;
		o.files = Object.fromEntries(Object.entries(this.files).map(([k, v]) => ([k, v.map(dexFile => dexFile.serialize())])));
		return o;
	}

	// deserializes an object into a Dexfile
	static deserialize(o)
	{
		const fileSet = new this();
		fileSet.root = o.root;
		fileSet.files = Object.fromEntries(Object.entries(o.files).map(([k, v]) => ([k, v.map(dexFile => DexFile.deserialize(dexFile))])));
		return fileSet;
	}

	pretty(prefix="")
	{
		const r = [];
		r.push(`${prefix}${xu.cf.fg.white("FileSet")} ${xu.cf.fg.cyan("(")}${xu.cf.fg.white("root ")}${xu.cf.fg.magentaDim(this.root)}${xu.cf.fg.cyan(")")} has ${xu.cf.fg.white(this.all.length.toLocaleString())} file${this.all.length===1 ? "" : "s"}:`);
		r.push(...this.all.map(f => f.pretty(`${prefix}\t`)));
		return r.join("\n");
	}

	// shortcut getters to return single/multi often used categories
	get all() { return Object.values(this.files).flat(); }
	get main() { return (this.files.main || [])[0]; }
	get aux() { return (this.files.aux || [])[0]; }
}
