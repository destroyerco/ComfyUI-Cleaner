
import json
import os
import glob
import re
import shutil
import argparse
from pathlib import Path

# --- Configuration ---
ALWAYS_KEEP = {
    "comfyui-manager",
    "ComfyUI-Manager",
    "ComfyUI-Custom-Scripts",
    "ComfyUI_frontend"
}

PRIMITIVE_TYPES = {
    "int", "float", "string", "boolean", "combo", "number", 
    "INT", "FLOAT", "STRING", "BOOLEAN", "any", "ANY", "*"
}

def get_comfy_root():
    # Try to find root by looking for main.py or folder_paths.py
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "main.py").exists() or (parent / "comfy").is_dir():
            return parent
    return current

def extract_node_types_from_workflows(workflow_dirs):
    used_types = set()
    for w_dir in workflow_dirs:
        for wf_path in glob.glob(os.path.join(w_dir, "**/*.json"), recursive=True):
            try:
                with open(wf_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Search for 'type' in all objects (handles various workflow versions)
                    def find_types(obj):
                        if isinstance(obj, dict):
                            if "type" in obj and isinstance(obj["type"], str):
                                used_types.add(obj["type"])
                            for v in obj.values():
                                find_types(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                find_types(item)
                    
                    find_types(data)
            except Exception:
                continue
    return used_types - PRIMITIVE_TYPES

def scan_custom_nodes(custom_nodes_path, used_types):
    extension_report = {}
    
    extensions = [d for d in os.listdir(custom_nodes_path) 
                 if os.path.isdir(os.path.join(custom_nodes_path, d)) and d != "__pycache__"]

    print(f"Analyzing {len(extensions)} extensions against {len(used_types)} nodes...")

    for ext in extensions:
        if ext.lower() in [k.lower() for k in ALWAYS_KEEP]:
            extension_report[ext] = {"status": "keep", "reason": "Always Keep list"}
            continue
            
        ext_path = os.path.join(custom_nodes_path, ext)
        found_node = None
        
        # Strategy: Look for node strings in any .py or .js files
        # This is a broad but safe way to detect if an extension *might* provide a node
        try:
            for root, _, files in os.walk(ext_path):
                if found_node: break
                for file in files:
                    if file.endswith(('.py', '.js', '.json')):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                for nt in used_types:
                                    # Look for node type as a string key or class mapping
                                    if f'"{nt}"' in content or f"'{nt}'" in content:
                                        found_node = nt
                                        break
                        except:
                            continue
        except:
            pass
            
        if found_node:
            extension_report[ext] = {"status": "used", "reason": f"Uses node: {found_node}"}
        else:
            extension_report[ext] = {"status": "unused", "reason": "No used node types found in source code"}

    return extension_report

def main():
    parser = argparse.ArgumentParser(description="ComfyUI Cleaner: Find and disable unused custom nodes.")
    parser.add_argument("--root", type=str, help="ComfyUI root directory")
    parser.add_argument("--backup", action="store_true", help="Move unused nodes to a backup folder")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Don't move anything, just report (default)")
    parser.add_argument("--yes", action="store_true", help="Confirm moving files without asking")
    
    args = parser.parse_args()
    
    root = Path(args.root) if args.root else get_comfy_root()
    custom_nodes_path = root / "custom_nodes"
    workflow_dirs = [root / "user" / "default" / "workflows", root / "pysssss-workflows"] # Common paths
    
    if not custom_nodes_path.exists():
        print(f"Error: Could not find custom_nodes at {custom_nodes_path}")
        return

    print(f"--- ComfyUI Cleaner ---")
    print(f"Root: {root}")
    
    used_types = extract_node_types_from_workflows([str(d) for d in workflow_dirs if d.exists()])
    report = scan_custom_nodes(str(custom_nodes_path), used_types)
    
    unused = [ext for ext, data in report.items() if data["status"] == "unused"]
    
    print("\n--- Unused Extensions ---")
    for ext in unused:
        print(f" [ ] {ext}")
        
    print(f"\nTotal: {len(unused)} unused extensions found.")

    if args.backup and not args.dry_run:
        backup_dir = root / "custom_nodes_backup"
        if not backup_dir.exists():
            backup_dir.mkdir()
            
        if not args.yes:
            confirm = input(f"Move {len(unused)} folders to {backup_dir}? (y/n): ")
            if confirm.lower() != 'y':
                return

        for ext in unused:
            src = custom_nodes_path / ext
            dst = backup_dir / ext
            try:
                if dst.exists(): shutil.rmtree(dst)
                shutil.move(str(src), str(dst))
                print(f"Moved {ext} to backup.")
            except Exception as e:
                print(f"Error moving {ext}: {e}")
    else:
        print("\nRun with --backup to move these to 'custom_nodes_backup'.")

if __name__ == "__main__":
    main()
