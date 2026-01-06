"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Download, Trash2, Loader2, AlertCircle, CheckCircle2, Play, DollarSign, Zap, FileText } from "lucide-react"
import type { Job } from "@/lib/api/types"
import { formatDistanceToNow } from "date-fns"
import { AudioPlayer } from "@/components/audio/audio-player"

interface JobCardProps {
  job: Job
  onDelete: (jobId: number) => void
}

import { useUser } from "@clerk/nextjs"

export function JobCard({ job, onDelete }: JobCardProps) {
  const { user } = useUser()
  const isAdmin = user?.primaryEmailAddress?.emailAddress === "potter.jason@gmail.com"

  const [deleting, setDeleting] = useState(false)
  const [showPlayer, setShowPlayer] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    await onDelete(job.id)
    setDeleting(false)
  }

  const getStatusConfig = () => {
    switch (job.status) {
      case "pending":
        return {
          badge: <Badge className="bg-muted text-muted-foreground">Pending</Badge>,
          icon: <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />,
          showProgress: false,
        }
      case "processing":
        return {
          badge: (
            <Badge className="bg-primary/20 text-primary border-primary/30">
              Processing {job.progress_percentage}%
            </Badge>
          ),
          icon: <Loader2 className="w-5 h-5 text-primary animate-spin" />,
          showProgress: true,
        }
      case "completed":
        return {
          badge: <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Completed</Badge>,
          icon: <CheckCircle2 className="w-5 h-5 text-green-400" />,
          showProgress: false,
        }
      case "failed":
        return {
          badge: <Badge className="bg-destructive/20 text-destructive border-destructive/30">Failed</Badge>,
          icon: <AlertCircle className="w-5 h-5 text-destructive" />,
          showProgress: false,
        }
      case "cancelled":
        return {
          badge: <Badge variant="outline">Cancelled</Badge>,
          icon: <AlertCircle className="w-5 h-5 text-muted-foreground" />,
          showProgress: false,
        }
    }
  }

  const statusConfig = getStatusConfig()

  return (
    <>
      <Card className="glass group hover:bg-card/70 transition-all duration-300 hover:shadow-xl hover:shadow-primary/10">
        <CardHeader className="space-y-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                {statusConfig.icon}
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="font-semibold truncate text-sm">{job.original_filename}</h3>
                <p className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                </p>
              </div>
            </div>
            {statusConfig.badge}
          </div>

          {statusConfig.showProgress && (
            <div className="space-y-2">
              <Progress value={job.progress_percentage} className="h-2" />
            </div>
          )}
        </CardHeader>

        <CardContent className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Voice Provider</span>
            <span className="font-medium capitalize">{job.voice_provider}</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Reading Speed</span>
            <span className="font-medium">{job.reading_speed}x</span>
          </div>

          {isAdmin && job.estimated_cost > 0 && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground flex items-center gap-1">
                <DollarSign className="w-3 h-3" />
                Cost
              </span>
              <span className="font-medium text-primary">${Number(job.estimated_cost || 0).toFixed(4)}</span>
            </div>
          )}
          {job.tokens_used !== undefined && job.tokens_used > 0 && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground flex items-center gap-1">
                <Zap className="w-3 h-3" />
                Tokens Used
              </span>
              <span className="font-medium">{job.tokens_used.toLocaleString()}</span>
            </div>
          )}
          {job.chars_processed !== undefined && job.chars_processed > 0 && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground flex items-center gap-1">
                <FileText className="w-3 h-3" />
                Characters
              </span>
              <span className="font-medium">{job.chars_processed.toLocaleString()}</span>
            </div>
          )}

          {job.error_message && (
            <div className="p-2 rounded-lg bg-destructive/10 border border-destructive/20">
              <p className="text-xs text-destructive">{job.error_message}</p>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex items-center gap-2">
          {job.status === "completed" && job.audio_s3_url && (
            <>
              <Button size="sm" onClick={() => setShowPlayer(true)} className="flex-1">
                <Play className="w-4 h-4 mr-2" />
                Play
              </Button>
              <Button asChild size="sm" variant="outline">
                <a href={job.audio_s3_url} download>
                  <Download className="w-4 h-4" />
                </a>
              </Button>
            </>
          )}

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" size="sm" className={job.status === "completed" ? "" : "flex-1"}>
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent className="glass-strong">
              <AlertDialogHeader>
                <AlertDialogTitle>Delete audiobook?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete "{job.original_filename}" and all associated files. This action cannot be
                  undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete} disabled={deleting} className="bg-destructive">
                  {deleting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Deleting...
                    </>
                  ) : (
                    "Delete"
                  )}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardFooter>
      </Card>

      {showPlayer && job.audio_s3_url && (
        <AudioPlayer audioUrl={job.audio_s3_url} title={job.original_filename} onClose={() => setShowPlayer(false)} />
      )}
    </>
  )
}
