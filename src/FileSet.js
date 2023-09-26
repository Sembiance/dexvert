import {xu, fg} from "xu";
import {path} from "std";
import {runUtil, fileUtil} from "xutil";
import {DexFile} from "./DexFile.js";

export class FileSet
{
	root = null;
	files = {};

	// builder to get around the fact that constructors can't be async
	static async create(root, ...typesFiles)
	{
		const fileSet = new this();
		fileSet.root = path.resolve(root);
		for(const [type, files] of typesFiles.chunk(2))
			await fileSet.addAll(type, Array.force(files));
		return fileSet;
	}

	async addAll(type, files)
	{
		// Creaet a set of existing absolute paths for this addAll operation. Helps vastly speed up adding tons of files by avoiding having to do a 'find' operation for every addition
		const existingAbsolutePaths = Object.fromEntries((this.files[type] || []).map(f => ([f.absolute, f])));
		for(const file of files)
			await this.add(type, file, existingAbsolutePaths);
		
		// Doing this below instead of the above would be faster probably, but would yield files being added potentially out of order, which might be important to maintain
		//await Promise.all(files.map(file => this.add(type, file)));
	}

	// adds the given file of type type. If o is already a Dexfile, don't need to await
	async add(type, o, existingAbsolutePaths)
	{
		if(!type)
			throw new TypeError(`No type specified, required.`);

		if(!(o instanceof DexFile || typeof o==="string"))
			throw new TypeError(`Can't add file ${o} to FileSet due to being an unknown type ${typeof o}`);

		this.files[type] ||= [];
		if(!Object.hasOwn(this, type))
			Object.defineProperty(this, type, {get : () => (this.files[type] || [])[0]});

		const dexFile = o instanceof DexFile ? o : await DexFile.create({root : this.root, rel : o.startsWith("/") ? path.relative(this.root, o) : o});
		if(dexFile.root!==this.root)
			throw new Error(`Can't add dex file ${o.pretty()} due to root not matching FileSet root: ${this.root}`);

		const existingDexFile = existingAbsolutePaths ? existingAbsolutePaths[dexFile.absolute] : this.files[type].find(file => file.absolute===dexFile.absolute);
		if(!existingDexFile)
		{
			if(existingAbsolutePaths)
				existingAbsolutePaths[dexFile.absolute] = dexFile;
			this.files[type].push(dexFile);
		}
		else
		{
			await existingDexFile.calcStats();	// if we try to add an existing file, it's possible the file has changed on disk, so let's re-calc it's stats
		}
	}

	// removes the given file from this FileSet. If unlink is set to true, also deletes it from the disk
	async remove(type, file, {unlink}={})
	{
		const absolutePath = file instanceof DexFile ? file.absolute : file;
		(this.files[type] || []).filterInPlace(v => v.absolute!==absolutePath);
		if(unlink)
			await fileUtil.unlink(absolutePath, {recursive : true});
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
	async clone(types)
	{
		const fileSet = await FileSet.create(this.root);
		for(const type of (types ? Array.force(types) : Object.keys(this.files)))
			await fileSet.addAll(type, (this.files[type] || []).map(file => file.clone()));
		return fileSet;
	}

	// removes all files of the given type from this fileSet
	removeType(type)
	{
		delete this.files[type];
	}

	// changes a type from oldType to newType
	changeType(oldType, newType)
	{
		for(const file of this.files[oldType])
			this.add(newType, file);
		this.removeType(oldType);
	}

	// rsync copies all files to targetRoot and returns a FileSet for the new root
	async rsyncTo(targetRoot, {type, relativeFrom, unlink}={})
	{
		const newFileSet = await this.clone(type ? [type] : null);
		if(relativeFrom)
			newFileSet.changeRoot(relativeFrom);

		const missingFilePaths = [];
		await (type ? (this.files[type] || []) : this.all).parallelMap(async file =>
		{
			const fileRel = relativeFrom ? path.relative(relativeFrom, file.absolute) : file.rel;
			if(fileRel.includes("/"))
				await Deno.mkdir(path.join(targetRoot, path.dirname(fileRel)), {recursive : true});
			const targetPath = path.join(targetRoot, file.isDirectory ? path.dirname(fileRel) : fileRel);
			await runUtil.run("rsync", ["-sa", path.join(relativeFrom || file.root, fileRel), targetPath]);

			if(!(await fileUtil.exists(targetPath)))
				missingFilePaths.push(targetPath);
		});

		newFileSet.changeRoot(targetRoot, {keepRel : true});

		// if rsync didn't copy over any files for whatever reason we want to remove it from the newFileSet
		// this can happen with the process server and 'auxFiles/otherDirs' as it creates and deletes other files in parallel, so can't depends on otherFiles/otherDirs to still be there
		if(missingFilePaths.length>0)
			newFileSet.all.filterInPlace(v => !missingFilePaths.includes(v.absolute));
		
		if(unlink)
			await Array.from(type ? (this.files[type] || []) : this.all).parallelMap(async file => await this.remove(type || "all", file, {unlink}));

		return newFileSet;
	}

	// converts this to a serilizable object
	serialize()
	{
		const o = {};
		o.root = this.root;
		o.files = Object.fromEntries(Object.entries(this.files).map(([k, v]) => ([k, v.map(dexFile => dexFile.serialize())])));
		return o;
	}

	pretty(prefix="")
	{
		let r = [];
		r.push(`${prefix}FileSet ${xu.paren(`root ${fg.magentaDim(this.root)}`)} has ${fg.yellowDim(this.all.length.toLocaleString())} file${this.all.length===1 ? "" : "s"}:`);
		if(this.all.length>0)
		{
			const longestType = Object.keys(this.files).map(v => v.length).max();
			for(const [type, typeFiles] of Object.entries(this.files))
				r = r.concat(typeFiles.map(f => f.pretty(`\n${prefix}\t${fg.white(`${type.padStart(longestType, " ")}: `)}`)));
		}
		return r.join("");
	}

	get all() { return Object.values(this.files).flat(); }
}
