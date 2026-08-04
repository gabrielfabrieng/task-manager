import { FormEvent, useState } from "react";
import { useTaskMutations } from "../hooks/useTasks";
import type { SharePermission } from "../types";

export function ShareDialog({ taskId, onClose }: { taskId: number; onClose: () => void }) {
  const { share } = useTaskMutations();
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<SharePermission>("view");
  const [error, setError] = useState<string | null>(null);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    share.mutate(
      { id: taskId, email, permission },
      {
        onSuccess: onClose,
        onError: () => setError("Could not share (unknown e-mail or already shared)."),
      },
    );
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} data-testid="share-dialog">
        <h3>Share task</h3>
        <form onSubmit={onSubmit}>
          <input
            data-testid="share-email"
            placeholder="Recipient e-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <select
            data-testid="share-permission"
            value={permission}
            onChange={(e) => setPermission(e.target.value as SharePermission)}
          >
            <option value="view">Can view</option>
            <option value="edit">Can edit</option>
          </select>
          {error && <p className="error">{error}</p>}
          <div className="modal-actions">
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit" data-testid="share-submit" disabled={share.isPending}>
              Share
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
