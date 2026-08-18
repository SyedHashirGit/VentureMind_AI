import { Crown, Cpu, Compass, Banknote, Megaphone, Swords, Scale, Gavel, type LucideIcon } from "lucide-react";

export const AGENT_META: Record<string, { label: string; icon: LucideIcon }> = {
  validation: { label: "The verdict", icon: Gavel },
  ceo: { label: "CEO", icon: Crown },
  cto: { label: "CTO", icon: Cpu },
  pm: { label: "Product", icon: Compass },
  investor: { label: "Investor", icon: Banknote },
  marketing: { label: "Marketing", icon: Megaphone },
  competitor: { label: "Competitor", icon: Swords },
  legal: { label: "Legal", icon: Scale },
};

export const agentMeta = (id: string) => AGENT_META[id] ?? { label: id, icon: Gavel };
