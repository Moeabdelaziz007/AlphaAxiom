'use client';

import React from 'react';
import { Bitcoin, Landmark, Coins } from 'lucide-react';
import { AssetType } from '@/lib/types';

interface AssetSelectorProps {
    activeAsset: AssetType;
    onAssetChange: (asset: AssetType) => void;
}

const assets = [
    { id: 'STOCKS' as AssetType, name: 'Stocks', icon: Landmark, color: 'blue-400' },
    { id: 'GOLD' as AssetType, name: 'Gold', icon: Coins, color: 'neon-gold' },
];

export default function AssetSelector({ activeAsset, onAssetChange }: AssetSelectorProps) {
    return (
        <div className="flex items-center gap-2">
            {assets.map((asset) => {
                const Icon = asset.icon;
                const isActive = activeAsset === asset.id;

                return (
                    <button
                        key={asset.id}
                        onClick={() => onAssetChange(asset.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium 
                                   transition-all btn-neon ${isActive
                                ? `bg-${asset.color}/20 text-${asset.color} border border-${asset.color}/50 
                                   shadow-[0_0_15px_rgba(0,242,234,0.2)]`
                                : 'glass-panel text-gray-500 hover:text-gray-300'
                            }`}
                    >
                        <Icon className={`w-4 h-4 ${isActive ? `text-${asset.color}` : ''}`} />
                        {asset.name}
                    </button>
                );
            })}
        </div>
    );
}
