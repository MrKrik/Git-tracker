package cmd

import (
	"github.com/spf13/cobra"
)

func NewRunCmd() *cobra.Command {
	runCmd := &cobra.Command{
		Use:   "run",
		Short: "Run programm",
		Run: func(cmd *cobra.Command, args []string) {
		},
	}
	return runCmd
}
