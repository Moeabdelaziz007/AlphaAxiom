"""
Hot-Reload System for AIX Skills
Watches the skills directory and reloads skills when files change
"""

import asyncio
import os
from pathlib import Path
from typing import Callable, Optional, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SkillWatcher:
    """Watches the skills directory for changes and triggers reloads"""
    
    def __init__(
        self,
        skills_dir: Path,
        on_reload: Callable[[], None],
        extensions: tuple = ('.aix', '.yaml', '.yml'),
        debounce_seconds: float = 1.0
    ):
        self.skills_dir = Path(skills_dir)
        self.on_reload = on_reload
        self.extensions = extensions
        self.debounce_seconds = debounce_seconds
        
        self._running = False
        self._last_reload = 0.0
        self._file_mtimes: dict = {}
        self._task: Optional[asyncio.Task] = None
    
    def start(self):
        """Start watching for file changes"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info(f"🔄 Skill hot-reload watching: {self.skills_dir}")
    
    def stop(self):
        """Stop watching"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
    
    async def _watch_loop(self):
        """Main watch loop - checks for file changes periodically"""
        # Initial scan
        self._scan_files()
        
        while self._running:
            try:
                await asyncio.sleep(1.0)  # Check every second
                
                if self._check_for_changes():
                    # Debounce - wait a bit for all changes to settle
                    now = datetime.now().timestamp()
                    if now - self._last_reload >= self.debounce_seconds:
                        logger.info("📦 Skills changed, triggering reload...")
                        self._last_reload = now
                        self._scan_files()  # Update mtimes
                        
                        try:
                            self.on_reload()
                            logger.info("✅ Skills reloaded successfully")
                        except Exception as e:
                            logger.error(f"❌ Skill reload failed: {e}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                await asyncio.sleep(5)  # Back off on errors
    
    def _scan_files(self):
        """Scan directory and record file modification times"""
        self._file_mtimes.clear()
        
        if not self.skills_dir.exists():
            return
        
        for ext in self.extensions:
            for filepath in self.skills_dir.glob(f"*{ext}"):
                try:
                    self._file_mtimes[str(filepath)] = filepath.stat().st_mtime
                except OSError:
                    pass
    
    def _check_for_changes(self) -> bool:
        """Check if any skill files have changed"""
        if not self.skills_dir.exists():
            return False
        
        current_files: Set[str] = set()
        has_changes = False
        
        for ext in self.extensions:
            for filepath in self.skills_dir.glob(f"*{ext}"):
                path_str = str(filepath)
                current_files.add(path_str)
                
                try:
                    mtime = filepath.stat().st_mtime
                    
                    # New file or modified file
                    if path_str not in self._file_mtimes:
                        logger.debug(f"New skill file: {filepath.name}")
                        has_changes = True
                    elif self._file_mtimes[path_str] != mtime:
                        logger.debug(f"Modified skill: {filepath.name}")
                        has_changes = True
                except OSError:
                    pass
        
        # Check for deleted files
        for path_str in list(self._file_mtimes.keys()):
            if path_str not in current_files:
                logger.debug(f"Deleted skill: {Path(path_str).name}")
                has_changes = True
        
        return has_changes


class HotReloadManager:
    """Manages hot-reloading of all reloadable components"""
    
    def __init__(self, skill_executor):
        self.skill_executor = skill_executor
        self.watchers: list = []
        self._started = False
    
    def setup(self):
        """Setup all watchers"""
        skills_dir = Path(self.skill_executor.loaded_skills.get('_path', './skills'))
        if not skills_dir.exists():
            skills_dir = Path(__file__).parent
        
        watcher = SkillWatcher(
            skills_dir=skills_dir,
            on_reload=self._reload_skills
        )
        self.watchers.append(watcher)
    
    def start(self):
        """Start all watchers"""
        if self._started:
            return
        
        self._started = True
        for watcher in self.watchers:
            watcher.start()
        
        logger.info("🔥 Hot-reload system started")
    
    def stop(self):
        """Stop all watchers"""
        self._started = False
        for watcher in self.watchers:
            watcher.stop()
        
        logger.info("Hot-reload system stopped")
    
    def _reload_skills(self):
        """Callback to reload skills"""
        try:
            old_count = len(self.skill_executor.loaded_skills)
            self.skill_executor.reload_skills()
            new_count = len(self.skill_executor.loaded_skills)
            
            logger.info(f"Skills reloaded: {old_count} → {new_count}")
        except Exception as e:
            logger.error(f"Failed to reload skills: {e}")
            raise
