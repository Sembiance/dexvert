import {xu, fg} from "xu";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import {runUtil} from "xutil";
import {DexFile} from "./DexFile.js";

export class FileSet
{
	root = null;
	files = {};

	// builder to get around the fact that constructors can't be async
	static async create(root, type, files)
	{
		const fileSet = new this();
		fileSet.root = path.resolve(root);
		if(type && files)
			await fileSet.addAll(type, Array.force(files));
		return fileSet;
	}

	// rsync copies all files to targetRoot and returns a FileSet for the new root
	async rsyncTo(targetRoot, {type}={})
	{
		const newFileSet = await this.clone();
		for(const file of (type ? this.files[type] : this.all))
		{
			if(file.rel.includes("/"))
				await Deno.mkdir(path.join(targetRoot, path.dirname(file.rel)), {recursive : true});
			await runUtil.run("rsync", ["-aL", path.join(this.root, file.rel), path.join(targetRoot, file.rel)]);
		}

		return newFileSet.changeRoot(targetRoot, {keepRel : true});
	}

	async addAll(type, files)
	{
		for(const file of files)
			await this.add(type, file);
		
		// Doing this would be faster probably, but would yield files being added potentially out of order, which might be important to maintain
		//await Promise.all(files.map(file => this.add(type, file)));
	}

	// adds the given file of type type
	async add(type, o)
	{
		if(!type)
			throw new TypeError(`No type specified, required.`);

		if(!(o instanceof DexFile || typeof o==="string"))
			throw new TypeError(`Can't add file ${o} to FileSet due to being an unknown type ${typeof o}`);

		if(!this.files[type])
		{
			Object.defineProperty(this, type, {get : () => (this.files[type] || [])[0]});
			this.files[type] = [];
		}

		const dexFile = o instanceof DexFile ? o : await DexFile.create({root : this.root, subPath : o.startsWith("/") ? path.relative(this.root, o) : o});
		if(dexFile.root!==this.root)
			throw new Error(`Can't add dex file ${o.pretty()} due to root not matching FileSet root: ${this.root}`);

		this.files[type].push(dexFile);
	}

	// changes the root location of this FileSet and the DexFiles within it
	changeRoot(newRoot, o={})
	{
		this.root = path.resolve(newRoot);
		for(const file of this.all)
			file.changeRoot(newRoot, o);
		
		return this;
	}

	// creates a copy of this
	async clone()
	{
		const fileSet = await FileSet.create(this.root);
		for(const [type, files] of Object.entries(this.files))
			await fileSet.addAll(type, files.map(file => file.clone()));
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
		r.push(`${prefix}${fg.white("FileSet")} ${fg.cyan("(")}${fg.white("root ")}${fg.magentaDim(this.root)}${fg.cyan(")")} has ${fg.white(this.all.length.toLocaleString())} file${this.all.length===1 ? "" : "s"}:`);
		if(this.all.length>0)
		{
			const longestType = Object.keys(this.files).map(v => v.length).max();
			for(const [type, typeFiles] of Object.entries(this.files))
				r.push(...typeFiles.map(f => f.pretty(`\n${prefix}\t${fg.white(`${type.padStart(longestType, " ")}: `)}`)));
		}
		return r.join("");
	}

	// shortcut getters to return single/multi often used categories
	get all() { return Object.values(this.files).flat(); }
	/*get input() { return (this.files.input || [])[0]; }
	get output() { return (this.files.output || [])[0]; }
	get new() { return (this.files.new || [])[0]; }
	get outDir() { return (this.files.outDir || [])[0]; }
	get homeDir() { return (this.files.homeDir || [])[0]; }
	get aux() { return (this.files.aux || [])[0]; }*/
}
