import {xu} from "xu";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import {runUtil} from "xutil";
import {DexFile} from "./DexFile.js";

export class FileSet
{
	root = null;
	files = {};

	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static async create(o)
	{
		if(!o)
			return null;

		const fileSet = new this({allowNew : true});

		function getRoot(v)
		{
			return (v instanceof DexFile ? v.root : (v.startsWith("/") ? path.dirname(v) : Deno.cwd()));
		}

		if(typeof o==="string")
		{
			// a string, assume we just have a single primary file, absolute path
			fileSet.root = getRoot(o);
			await fileSet.add("primary", path.basename(o));
		}
		else if(o instanceof DexFile)
		{
			// a single DexFile, assume it's a primary file
			fileSet.root = o.root;
			await fileSet.add("primary", o);
		}
		else if(Array.isArray(o))
		{
			// an array, assume it's an array of primary files
			fileSet.root = o.map(getRoot).sortMulti([v => v.length])[0];
			for(const v of o)
				await fileSet.add("primary", path.relative(fileSet.root, v));
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
			for(const [type, files] of Object.entries(o.files))
			{
				for(const file of files)
					await fileSet.add(type, file);
			}
		}

		return fileSet;
	}

	// rsync copies all files to targetRoot and returns a FileSet for the new root
	async rsyncTo(targetRoot)
	{
		for(const file of this.all)
		{
			if(file.rel.includes("/"))
				await Deno.mkdir(path.join(targetRoot, path.dirname(file.rel)), {recurisve : true});
			await runUtil.run("rsync", ["-aL", path.join(this.root, file.rel), path.join(targetRoot, file.rel)]);
		}

		return this.clone().changeRoot(targetRoot);
	}

	async addAll(type, files)
	{
		await Promise.all(files.map(file => this.add(type, file)));
	}

	// adds the given file of type type
	async add(_type, _o)
	{
		const type = typeof _o==="undefined" ? "primary" : _type;
		const o = typeof _o==="undefined" ? _type : _o;

		if(!this.files[type])
			this.files[type] = [];

		if(o instanceof DexFile)
			this.files[type].push(o);
		else if(typeof o==="string")
			this.files[type].push(await DexFile.create({root : this.root, subPath : o.startsWith("/") ? path.relative(this.root, o) : o}));
		else
			throw new Error(`Can't add file ${o} to FileSet due to being an unknown type ${typeof o}`);
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
		const fileSet = new FileSet({allowNew : true});
		fileSet.root = this.root;
		fileSet.files = Object.fromEntries(Object.entries(this.files).map(([k, subFiles]) => ([k, subFiles.map(subFile => subFile.clone())])));
		return fileSet;
	}

	// shortcut getters to return single/multi often used categories
	get all() { return Object.values(this.files).flat(); }
	get allFull() { return this.all.map(v => path.join(this.root, v)); }

	get primary() { return this.primaries[0]; }
	get primaryFull() { return path.join(this.root, this.primary); }

	get primaries() { return (this.files.primary || []); }
	get primariesFull() { return this.primaries.map(v => path.join(this.root, v)); }

	get aux() { return this.auxes[0]; }
	get auxFull() { return path.join(this.root, this.aux); }

	get auxes() { return (this.files.aux || []); }
	get auxesFull() { return this.auxes.map(v => path.join(this.root, v)); }

	get original() { return this.originals[0]; }
	get originalFull() { return path.join(this.root, this.original); }

	get originals() { return (this.files.original || []); }
	get originalsFull() { return this.originals.map(v => path.join(this.root, v)); }
}
