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

		if(typeof o==="string")
		{
			// a string, assume we just have a single primary file
			fileSet.root = path.dirname(o);
			fileSet.files.primary = [path.basename(o)];
		}
		else if(Array.isArray(o))
		{
			// an array, assume it's an array of primary files
			fileSet.root = o.map(v => path.dirname(v)).sortMulti([v => v.length])[0];
			fileSet.files.primary = o.map(v => path.relative(fileSet.root, v));
		}
		else if(!Object.hasOwn(o, "root"))
		{
			// an object without a root
			fileSet.root = Object.values(o).flatMap(v => Array.force(v)).map(v => path.dirname(v)).sortMulti([v => v.length])[0];
			for(const [type, files] of Object.entries(o))
				fileSet.files[type] = Array.force(files).map(v => path.relative(fileSet.root, v));
		}
		else
		{
			fileSet.root = path.resolve(o.root);
			Object.assign(fileSet.files, o.files);
		}

		if(!Object.hasOwn(o, "root") && fileSet.root===".")
			fileSet.root = Deno.cwd();

		// convert files into DexFile objects
		for await(const [type, subPaths] of Object.entries(fileSet.files))
			fileSet.files[type] = await Promise.all(subPaths.map(async file => await DexFile.create({root : fileSet.root, subPath : file})));

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
}
