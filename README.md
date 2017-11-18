# Version Minecraft worlds with Git

I was somewhat annoyed that to back up my Minecraft world, I have to store a
full copy of it, even if it changed just a little. If we are so good at
versioning code why, can't we version Minecraft worlds?

This quick and somewhat dirty script converts Minecraft worlds into a textual
representation that can be checked into a git repository. This works because
both traditional and delta compression is aplied to objects in Git. However, as
of now, there is no way to decode such a file into a Minecraft world.

Todo:
* Minimize the disk usage by not keeping around the whole working tree
* Decoding
* Experiment with binary formats
